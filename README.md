# Kubernetes_G1_1
Tìm hiểu Kubernetes và Deploy WordPress Instance trên Kubernetes
# Steps and Commands to install k8s:

(This assumes you have 3 servers up and running)

## 1. On each server, install Docker
(Installation guide: https://docs.docker.com/engine/install/ubuntu/)

### Set up the repository: 

- Update the `apt` package index and install packages to allow `apt` to use a repository over HTTPS:

```
sudo apt install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```
- Add Docker’s official GPG key:
```
curl -fsSL hhttps://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```
- Sử dụng lệnh sau đây để thiết lập kho lưu trữ ổn định:

```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
### Install Docker engine

```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"


sudo apt update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

Note: Nếu gặp lỗi không có tài nguyên hoặc đang bị sử dụng :
```
E: Could not get lock /var/lib/dpkg/lock-frontend - open (11: Resource temporarily unavailable)  
E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend),   
 is another process using it?
```

Tạo file bằng cách `sudo vi /etc/docker/daemon.json`

Thêm vào file: 
```
{
"exec-opts": ["native.cgroupdriver=systemd"],
"log-driver": "json-file",
"log-opts": {
"max-size": "100m"
},
"storage-driver": "overlay2"
}
```
Run in terminal: 
```
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet
```


## 2. Trên mỗi VM server

### Đảm bảo rằng br_netfilter module được loaded. Kiểm tra bằng `lsmod | grep br_netfilter` hoặc  `sudo modprobe br_netfilter`

Tiếp theo: 

```
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF

sudo sysctl --system
```

### Disable Swap và Enable Kernel modules

- Tắt swap
```
docker info | grep Cgroup
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
sudo swapoff -a
```
- Bật kernel modules and configure sysctl
```
sudo modprobe overlay
sudo modprobe br_netfilter
```
- Reload sysctl
```
sudo sysctl --system
```

## 3. On each server, install kubernetes
(Installation guide: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)

- Update `apt` package và install packages cần thiết: 
```
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl
```

- Download the Google Cloud public signing key:
```
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
```

- Add the Kubernetes apt repository: 
```
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

- Update lại và install kubelet, kubeadm and kubectl

```
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

## 4. On the Master server only, initialize the cluster

### Khởi tạo master Node bằng kubeadm

```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

Sau khi câu lệnh kết thúc command, copy kubeadm join provided:

```
sudo kubeadm join <ip_v4_private>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<chuỗi hash>
```

## 5. On the Master server only, set up the kubernetes configuration file for general usage

```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
Alternatively, if you are the root user, you can run:
```
export KUBECONFIG=/etc/kubernetes/admin.conf
```

## 6. On the Master server only, apply a common networking plugin. In this case, Flannel

```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml
```

## 7. On the Worker servers only, join them to the cluster using the command you copied earlier in step 4

```
kubeadm join <ip-private-master-node>:6443 --token ... --discovery-token-ca-cert-hash ...
```
Ví dụ: 
```
sudo kubeadm join 172.31.4.17:6443 --token 9c9ryi.ze5ay9o8kxclmlp7 \
        --discovery-token-ca-cert-hash sha256:489b33cb70bd1588dca842012536db43af9acb1d3c35ed9721eac1add7924c23
```
- Kết quả thu được như sau 
```
:~ $ kubectl get nodes
NAME              STATUS   ROLES                  AGE     VERSION
ip-172-31-4-17    Ready    control-plane,master   2m22s   v1.23.6
ip-172-31-8-126   Ready    <none>                 34s     v1.23.6
ip-172-31-8-248   Ready    <none>                 30s     v1.23.6
```

Vậy là bạn đã hoàn thành cài đặt k8s cluster bằng kubeadm





