# 📦 EMM – Falha de Build por Artefato Ausente no Nexus e Cache Maven Obsoleto

## 🇧🇷 Português (BR)

**issue:**
Após a renovação automática de certificados (novos JKS gerados e enviados ao Object Storage), o pipeline de build/deploy do EMM travou: o step de build tentava baixar uma dependência (`witchcraft`, POM/JAR) que não existia mais no novo servidor Nexus.

**causa raiz:**
O artefato `br.com.navita:witchcraft:1.0.78-EMM-SNAPSHOT` (e seu módulo witchcraft-data) não tinha sido migrado para o novo Nexus. Mesmo depois de o artefato ser recuperado do Nexus antigo e re-publicado no novo, o build continuava falhando pelo mesmo motivo, porque os runners de CI mantinham o artefato ausente em cache local do Maven (~/.m2), então nunca chegavam a baixar a versão nova disponível no Nexus.

**solução:**
O maven-metadata.xml e os artefatos (JAR/POM) do witchcraft-data foram recuperados do Nexus antigo (`nexus-teste.navita.com.br`) e re-enviados via curl para o novo Nexus (`nexus.navita.com.br`). Como o build ainda falhava por causa do cache local, foi feito acesso aos runners de CI e executado `rm -rf ~/.m2/repository/br/com/navita/witchcraft-data` para forçar o download da versão correta na próxima execução. Com o cache limpo, o pipeline de build/deploy foi executado com sucesso.

---

## 🇺🇸 English

**issue:**
After an automatic certificate renewal (new JKS files generated and uploaded to Object Storage), the EMM build/deploy pipeline got stuck: the build step tried to download a dependency (`witchcraft`, POM/JAR) that no longer existed on the new Nexus server.

**root cause:**
The `br.com.navita:witchcraft:1.0.78-EMM-SNAPSHOT` artifact (and its witchcraft-data module) hadn't been migrated to the new Nexus. Even after the artifact was recovered from the old Nexus and re-published to the new one, the build kept failing for the same reason, because the CI runners kept the missing artifact cached locally in Maven's ~/.m2, so they never actually downloaded the new version now available on Nexus.

**solution:**
The maven-metadata.xml and the witchcraft-data artifacts (JAR/POM) were recovered from the old Nexus (`nexus-teste.navita.com.br`) and re-uploaded via curl to the new Nexus (`nexus.navita.com.br`). Since the build still failed because of the local cache, the CI runners were accessed directly and `rm -rf ~/.m2/repository/br/com/navita/witchcraft-data` was run to force a fresh download on the next run. With the cache cleared, the build/deploy pipeline ran successfully.

---

## 🇪🇸 Español

**issue:**
Tras una renovación automática de certificados (nuevos JKS generados y subidos al Object Storage), el pipeline de build/deploy de EMM quedó bloqueado: el paso de build intentaba descargar una dependencia (`witchcraft`, POM/JAR) que ya no existía en el nuevo servidor Nexus.

**causa raíz:**
El artefacto `br.com.navita:witchcraft:1.0.78-EMM-SNAPSHOT` (y su módulo witchcraft-data) no había sido migrado al nuevo Nexus. Incluso después de recuperar el artefacto del Nexus antiguo y volver a publicarlo en el nuevo, el build seguía fallando por el mismo motivo, porque los runners de CI mantenían el artefacto faltante en caché local de Maven (~/.m2), por lo que nunca llegaban a descargar la versión nueva disponible en Nexus.

**solución:**
El maven-metadata.xml y los artefactos (JAR/POM) de witchcraft-data se recuperaron del Nexus antiguo (`nexus-teste.navita.com.br`) y se volvieron a subir vía curl al nuevo Nexus (`nexus.navita.com.br`). Como el build seguía fallando por la caché local, se accedió directamente a los runners de CI y se ejecutó `rm -rf ~/.m2/repository/br/com/navita/witchcraft-data` para forzar la descarga de la versión correcta en la siguiente ejecución. Con la caché limpia, el pipeline de build/deploy se ejecutó con éxito.
