# Ansible Collection - stevefulme1.lambdalabs

Manage Lambda Labs GPU cloud resources with Ansible -- instances, clusters, persistent filesystems, firewall rules, SSH keys, and ML/AI operational workflows.

This collection provides **30 modules**, a **dynamic inventory plugin**, an **EDA event source**, and **10 roles** for GPU infrastructure and ML operations.

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.10 |
| Ansible Core | >= 2.16 |

No additional Python libraries are required -- all API calls use `ansible.module_utils.urls`.

## Installation

```bash
ansible-galaxy collection install stevefulme1.lambdalabs
```

Install from source:

```bash
ansible-galaxy collection install git+https://github.com/stevefulme1/ansible-lambdalabs.git
```

## Authentication

Every module requires an `api_key` parameter. You can also set it via the `LAMBDA_API_KEY` environment variable.

```yaml
# group_vars/all.yml
lambda_api_key: "{{ vault_lambda_api_key }}"
```

| Parameter | Description | Required | Env Variable |
|---|---|---|---|
| `api_key` | Lambda Labs API key | Yes | `LAMBDA_API_KEY` |
| `timeout` | Request timeout in seconds (default: `30`) | No | -- |

## Quick Start

### Launch a GPU instance

```yaml
- name: Launch an A100 instance
  stevefulme1.lambdalabs.instance:
    api_key: "{{ lambda_api_key }}"
    state: present
    instance_type_name: gpu_1x_a100_sxm4
    region_name: us-east-1
    name: training-node-01
    ssh_key_names:
      - my-ssh-key
  register: instance

- name: Show instance IP
  ansible.builtin.debug:
    msg: "Instance {{ instance.id }} at {{ instance.ip }}"
```

### Launch a multi-node GPU cluster

```yaml
- name: Launch 4-node training cluster
  stevefulme1.lambdalabs.cluster:
    api_key: "{{ lambda_api_key }}"
    state: present
    instance_type_name: gpu_8x_h100_sxm5
    region_name: us-south-1
    quantity: 4
    ssh_key_names:
      - cluster-key
  register: cluster

- name: Wait for all nodes to be active
  stevefulme1.lambdalabs.instance_wait:
    api_key: "{{ lambda_api_key }}"
    instance_id: "{{ item }}"
    target_state: active
    timeout: 600
  loop: "{{ cluster.instance_ids }}"
```

### Attach persistent storage and check pricing

```yaml
- name: Create a persistent filesystem
  stevefulme1.lambdalabs.filesystem:
    api_key: "{{ lambda_api_key }}"
    state: present
    name: training-data
    region: us-east-1
  register: fs

- name: Attach filesystem to instance
  stevefulme1.lambdalabs.filesystem_attach:
    api_key: "{{ lambda_api_key }}"
    filesystem_id: "{{ fs.id }}"
    instance_ids:
      - "{{ instance.id }}"

- name: Check current GPU pricing
  stevefulme1.lambdalabs.instance_pricing_info:
    api_key: "{{ lambda_api_key }}"
  register: pricing
```

## Module Index

### Instances

| Module | Description |
|---|---|
| `instance` | Launch or terminate Lambda Labs GPU instances |
| `instance_info` | List or get Lambda Labs instance details |
| `instance_type_info` | List available Lambda Labs GPU instance types |
| `instance_availability_info` | Check real-time GPU availability by type and region |
| `instance_pricing_info` | Get current pricing per instance type |
| `instance_restart` | Restart a Lambda Labs instance |
| `instance_wait` | Wait for a Lambda Labs instance to reach a target state |
| `instance_tag` | Update instance tags and metadata |

### Clusters

| Module | Description |
|---|---|
| `cluster` | Launch multi-node GPU cluster |
| `cluster_info` | List cluster instances |
| `cluster_health_info` | Check cluster health |
| `cluster_scale` | Scale cluster up or down |
| `cluster_terminate` | Terminate all instances in a cluster |

### Filesystems

| Module | Description |
|---|---|
| `filesystem` | Create or delete persistent filesystems |
| `filesystem_info` | List Lambda Labs filesystems |
| `filesystem_attach` | Attach filesystem to instance |
| `filesystem_detach` | Detach filesystem from instance |
| `filesystem_snapshot` | Create or delete filesystem snapshots |
| `filesystem_usage_info` | Get filesystem usage statistics |

### Firewall

| Module | Description |
|---|---|
| `firewall_rule` | Add or remove firewall rules |
| `firewall_rule_info` | List firewall rules for an instance |
| `firewall_enable` | Enable firewall on instance |
| `firewall_disable` | Disable firewall on instance |

### SSH Keys

| Module | Description |
|---|---|
| `ssh_key` | Add or delete Lambda Labs SSH keys |
| `ssh_key_info` | List Lambda Labs SSH keys |
| `ssh_key_generate` | Generate a new SSH key pair via Lambda Labs API |
| `ssh_key_import` | Import SSH key from file path |

### Account

| Module | Description |
|---|---|
| `api_key_info` | Validate API key and get account info |
| `api_key_usage_info` | Get API usage statistics |
| `region_info` | List available regions |

## Dynamic Inventory

The collection includes a dynamic inventory plugin that queries the Lambda Labs API and groups instances by type, region, and status.

```yaml
# lambda_inventory.yml
plugin: stevefulme1.lambdalabs.lambda_inventory
api_key: "{{ lookup('env', 'LAMBDA_API_KEY') }}"
```

```bash
ansible-inventory -i lambda_inventory.yml --graph
```

## Event-Driven Ansible (EDA)

### Event Source: `lambda_events`

Polls the Lambda Labs API for instance state changes and emits events for automation triggers.

Events emitted: `instance_launched`, `instance_terminated`, `instance_error`, `gpu_degraded`.

```yaml
# eda-rulebook.yml
- name: React to Lambda Labs events
  hosts: all
  sources:
    - stevefulme1.lambdalabs.lambda_events:
        api_key: "{{ lambda_api_key }}"
        poll_interval: 60
  rules:
    - name: Auto-cleanup terminated instances
      condition: event.type == "instance_terminated"
      action:
        run_playbook:
          name: cleanup_instance.yml

    - name: Alert on GPU degradation
      condition: event.type == "gpu_degraded"
      action:
        run_playbook:
          name: gpu_alert.yml
```

## Roles

The collection includes 10 roles for ML/AI infrastructure and operations.

| Role | Description |
|---|---|
| `cuda_setup` | Install NVIDIA drivers and CUDA toolkit |
| `pytorch_environment` | Set up PyTorch training environment |
| `distributed_training` | Configure multi-node distributed training |
| `vllm_inference` | Deploy vLLM inference server |
| `jupyter_server` | Deploy JupyterLab server |
| `mlflow_tracking` | Set up MLflow tracking server |
| `model_checkpoint` | Automated model checkpoint management |
| `gpu_health_monitor` | Monitor GPU health metrics |
| `cost_tracker` | Track Lambda Labs instance costs |
| `idle_cleanup` | Auto-terminate idle GPU instances |

### Example: Set up a training node

```yaml
- name: Prepare GPU training environment
  hosts: gpu_instances
  roles:
    - role: stevefulme1.lambdalabs.cuda_setup
    - role: stevefulme1.lambdalabs.pytorch_environment
      vars:
        pytorch_version: "2.3"
        cuda_version: "12.4"
    - role: stevefulme1.lambdalabs.mlflow_tracking
      vars:
        mlflow_tracking_uri: "http://mlflow.internal:5000"
    - role: stevefulme1.lambdalabs.gpu_health_monitor
```

### Example: Deploy inference server

```yaml
- name: Deploy vLLM inference endpoint
  hosts: inference_nodes
  roles:
    - role: stevefulme1.lambdalabs.vllm_inference
      vars:
        model_name: "meta-llama/Llama-3-70b"
        tensor_parallel_size: 8
        max_model_len: 8192
```

## Contributing

Contributions are welcome. Please open an issue or pull request on
[GitHub](https://github.com/stevefulme1/ansible-lambdalabs).

## License

GNU General Public License v3.0 -- see [LICENSE](LICENSE) for details.
