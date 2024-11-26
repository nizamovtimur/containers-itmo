# Установка minicube
[Link](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew)

To install the latest minikube stable release on ARM64 macOS using Homebrew:

If the Homebrew Package Manager is installed:
```bash
brew install minikube
```

* Для запуска кластера из одной ноды:
```bash
minikube start --nodes 1 -p k8cluster
```

* Для остановки кластера из одной ноды:
```bash
minikube stop
```

* Для удаление кластера:
```bash
minikube delete --all
```

* Для получения информации о кластере:
```bash
kubectl get nodes
```