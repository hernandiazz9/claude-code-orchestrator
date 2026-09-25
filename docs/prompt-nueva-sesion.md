/grill-me

Quiero crear desde cero una skill de Claude Code llamada `orchestrator`. Usá la skill grill-me para entrevistarme hasta que tengamos el diseño completo, y recién después de que yo confirme que llegamos a un entendimiento compartido, escribí la skill.

Idioma: charlamos en español, pero la skill, sus archivos, nombres y todo lo que se escriba va en inglés.

La idea general: un orquestador con el que yo armo, en una entrevista estilo grill-me, un buen plan de unos 10 encargos. Después el orquestador los lanza como agentes, espera a que terminen y sigue solo con el siguiente, sin gastar su propio contexto en el trabajo de cada encargo. Sólo vuelve a mí al terminar el plan, o antes si algo falla o necesita una decisión mía; en ese caso sigue con lo que no dependa de eso y me escribe por Telegram, y yo puedo contestar desde Telegram.

Ya hay 11 decisiones tomadas en `docs/orchestrator-design.md` de esta carpeta. Leelo primero y no las vuelvas a preguntar, salvo que encuentres una contradicción. Seguí anotando ahí cada decisión nueva, numerada, a medida que la tomamos.

Preguntas que quedaron abiertas, para la primera ronda (tenían recomendación, pero no las contesté):
1. Dónde vive y cómo se instala: la fuente en esta carpeta bajo git, con enlaces desde ~/.claude/skills para orchestrator, grill-me y grilling.
2. Nombre `orchestrator` e invocación `/orchestrator`; qué pasa con la skill vieja `~/.claude/skills/orquestador`.
3. Qué campos lleva cada encargo en el plan.
4. Qué devuelve el agente al terminar (sólo su mensaje final con formato fijo, o un informe en archivo).
5. Qué decisiones son mías y cuáles puede tomar el orquestador.
6. Cuándo suena Telegram (primero en pantalla y a los 10 minutos por Telegram, o siempre).
7. Qué me entrega el orquestador al terminar el plan.
8. Qué pasa con los proyectos que ya usan el método viejo (kinelab, yazmina-people, andrevallenails).

Contexto que te sirve sin tener que preguntarme:
- La skill vieja está en `~/.claude/skills/orquestador`. No es la base: no copies sus reglas. Si alguna trampa que ella documenta te parece importante, planteala como pregunta.
- Mi bot de Telegram ya existe; su config está en `/Users/heralc/Desktop/HDDev/H-VOICE-CREEATOR/config.json` (sección telegram). Nunca imprimas el token.
- grill-me y grilling están instaladas en `.agents/skills/` de esta carpeta y enlazadas desde `.claude/skills/`.
