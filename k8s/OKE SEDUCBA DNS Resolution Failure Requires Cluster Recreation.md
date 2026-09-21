# 🌐 OKE SEDUCBA – Falha de Resolução DNS Exige Recriação do Cluster

## 🇧🇷 Português (BR)

**issue:**
Durante a migração do MCP (Mobile Config Provider), o provisionamento no ambiente SEDUCBA apresentou lentidão severa: os serviços do EMM no cluster OKE falhavam intermitentemente ao resolver nomes DNS, tanto públicos quanto internos.

**causa raiz:**
O CoreDNS estava tratando registros DNS públicos como se fossem serviços internos do cluster, aplicando sufixos de busca incorretos (.svc.cluster.local e .cluster.local) em vez do domínio correto (.navita.com.br) — rastreado a uma configuração de search DNS incorreta nos pods, confirmada via logs do CoreDNS, do DNS endpoint e da VCN.

**solução:**
Uma tentativa de corrigir via atualização de versão do cluster (para recriar o CoreDNS) travou no meio do processo, exigindo abertura de chamado (SR) com a Oracle Cloud para desbloquear a atualização. Diante disso, o cluster OKE SEDUCBA inteiro foi deletado e reimplantado do zero via Terraform, com todos os serviços. Na nova implantação, a política de DNS do EMM foi configurada explicitamente como ClusterFirst, apontando apenas para o DNS endpoint 10.10.1.190 com domínio de busca navita.com.br — eliminando a resolução incorreta e restaurando o ambiente.

---

## 🇺🇸 English

**issue:**
During the MCP (Mobile Config Provider) migration, provisioning in the SEDUCBA environment showed severe slowness: EMM services on the OKE cluster intermittently failed to resolve DNS names, both public and internal.

**root cause:**
CoreDNS was treating public DNS records as if they were internal cluster services, applying incorrect search suffixes (.svc.cluster.local and .cluster.local) instead of the correct domain (.navita.com.br) — traced to an incorrect DNS search configuration on the pods, confirmed via CoreDNS logs, the DNS endpoint, and the VCN.

**solution:**
An attempt to fix it by upgrading the cluster version (to recreate CoreDNS) got stuck mid-process, requiring an Oracle Cloud support case (SR) to unblock the upgrade. Given that, the entire SEDUCBA OKE cluster was deleted and redeployed from scratch via Terraform, including all services. In the new deployment, EMM's DNS policy was explicitly set to ClusterFirst, pointing only to the 10.10.1.190 DNS endpoint with navita.com.br as the search domain — eliminating the incorrect resolution and restoring the environment.

---

## 🇪🇸 Español

**issue:**
Durante la migración del MCP (Mobile Config Provider), el aprovisionamiento en el entorno SEDUCBA presentó una lentitud severa: los servicios de EMM en el clúster OKE fallaban intermitentemente al resolver nombres DNS, tanto públicos como internos.

**causa raíz:**
CoreDNS estaba tratando registros DNS públicos como si fueran servicios internos del clúster, aplicando sufijos de búsqueda incorrectos (.svc.cluster.local y .cluster.local) en lugar del dominio correcto (.navita.com.br) — rastreado a una configuración de search DNS incorrecta en los pods, confirmada mediante logs de CoreDNS, del DNS endpoint y de la VCN.

**solución:**
Un intento de corregirlo actualizando la versión del clúster (para recrear CoreDNS) quedó atascado a mitad de proceso, requiriendo abrir un caso de soporte (SR) con Oracle Cloud para desbloquear la actualización. Ante esto, todo el clúster OKE SEDUCBA fue eliminado y redesplegado desde cero vía Terraform, incluyendo todos los servicios. En el nuevo despliegue, la política de DNS de EMM se configuró explícitamente como ClusterFirst, apuntando solo al DNS endpoint 10.10.1.190 con dominio de búsqueda navita.com.br — eliminando la resolución incorrecta y restaurando el entorno.
