## Git
1. git status — что изменилось
2. git add — добавить в индекс
3. git commit — сохранить снимок
4. git push — отправить на GitHub
5. git pull — забрать изменения

## Git Flow
1. main — прод
2. develop — интеграция
3. feature/* — фича от develop
4. release/* — подготовка релиза
5. hotfix/* — срочная правка от main

## Таблица
| Ветка | Откуда | Куда | Зачем |
|-------|--------|------|-------|
| main | — | release/hotfix | прод |
| develop | main | feature/release | интеграция |
| feature/* | develop | develop | фича |
| release/* | develop | main+develop | релиз |
| hotfix/* | main | main+develop | срочный фикс |