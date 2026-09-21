# 🔁 AMAPI PROD V2 – Loop de Requests por Rate Limit da Google e Mensagem Travada no RabbitMQ

## 🇧🇷 Português (BR)

**issue:**
O ambiente AMAPI PROD V2 entrou em loop de requests: a fila principal (nvt-amapi.web-application.created.nvt-amapi-orchestrator-queue) parou de processar mensagens, e mais de 70 mil mensagens se acumularam na DLQ correspondente.

**causa raiz:**
Um rate limit (409 Too Many Requests) na Android Management API do Google fez uma mensagem de processamento falhar e ficar presa em estado UNACKED na fila principal. Como essa mensagem nunca era confirmada (ack) nem descartada, ela bloqueava o processamento de toda a fila, gerando o loop e o acúmulo de mensagens na DLQ (fluxo entre CORE / AMAPI Backend / Orchestrator).

**solução:**
Como medida imediata, todos os serviços envolvidos (CORE, AMAPI Backend, Orchestrator) foram parados para impedir novos processamentos e interromper o loop. Usando a API HTTP do RabbitMQ (endpoint /queues/.../get), a mensagem presa em UNACKED foi retirada da fila com ack_requeue_false, efetivamente descartando-a, e a fila foi então purgada antes de reiniciar os serviços. Após essas ações, o ambiente AMAPI PROD V2 voltou a operar normalmente.

---

## 🇺🇸 English

**issue:**
The AMAPI PROD V2 environment entered a request loop: the main queue (nvt-amapi.web-application.created.nvt-amapi-orchestrator-queue) stopped processing messages, and over 70,000 messages piled up in its corresponding DLQ.

**root cause:**
A rate limit (409 Too Many Requests) from Google's Android Management API caused a message to fail processing and get stuck in UNACKED state on the main queue. Since that message was never acknowledged or discarded, it blocked processing for the entire queue, causing the loop and the DLQ buildup (across the CORE / AMAPI Backend / Orchestrator flow).

**solution:**
As an immediate measure, all involved services (CORE, AMAPI Backend, Orchestrator) were stopped to prevent further processing and break the loop. Using RabbitMQ's HTTP API (the /queues/.../get endpoint), the stuck UNACKED message was pulled off the queue with ack_requeue_false, effectively discarding it, and the queue was then purged before restarting the services. After these actions, the AMAPI PROD V2 environment returned to normal operation.

---

## 🇪🇸 Español

**issue:**
El entorno AMAPI PROD V2 entró en un loop de requests: la cola principal (nvt-amapi.web-application.created.nvt-amapi-orchestrator-queue) dejó de procesar mensajes, y se acumularon más de 70 mil mensajes en su DLQ correspondiente.

**causa raíz:**
Un rate limit (409 Too Many Requests) de la Android Management API de Google hizo que un mensaje fallara en su procesamiento y quedara atascado en estado UNACKED en la cola principal. Como ese mensaje nunca era confirmado (ack) ni descartado, bloqueaba el procesamiento de toda la cola, generando el loop y la acumulación de mensajes en la DLQ (en el flujo entre CORE / AMAPI Backend / Orchestrator).

**solución:**
Como medida inmediata, se detuvieron todos los servicios involucrados (CORE, AMAPI Backend, Orchestrator) para evitar nuevos procesamientos e interrumpir el loop. Usando la API HTTP de RabbitMQ (endpoint /queues/.../get), el mensaje atascado en UNACKED fue retirado de la cola con ack_requeue_false, descartándolo efectivamente, y luego se purgó la cola antes de reiniciar los servicios. Tras estas acciones, el entorno AMAPI PROD V2 volvió a operar con normalidad.
