# Отчёт по задаче TZ-TF-01 (Sprint 0)

**Студент:** Danon-1ch
**Репозиторий:** https://github.com/Danon-1ch/InternetTechnologies

## 1. Ветки в репозитории

$ git branch -a
  develop
  feature/Danon-1ch-intro
* feature/Danon-1ch-report
  hotfix/Danon-1ch-typo
  main
<img width="356" height="89" alt="git branch -a" src="https://github.com/user-attachments/assets/6d073901-be2c-473e-a383-709fa482b412" />

## 2. PR фичи

- **PR #1:** feature/Danon-1ch-intro → develop
- Ссылка: https://github.com/Danon-1ch/InternetTechnologies/pull/1
- Файлы: students/Danon-1ch/ABOUT.md, NOTES.md, .env.example

## 3. Hotfix

- **PR #2:** hotfix/Danon-1ch-typo → main
- **PR #3:** hotfix/Danon-1ch-typo → develop
- Ссылки: https://github.com/Danon-1ch/InternetTechnologies/pull/2 https://github.com/Danon-1ch/InternetTechnologies/pull/3
- Правка: опечатка в sandbox/hello.txt (`wrold` → `world`)

## 4. Граф истории

$ git log --oneline --graph --all
* e05f7d0 (HEAD -> feature/Danon-1ch-report, origin/feature/Danon-1ch-report) docs: add git flow report
*   c18b1a3 (origin/develop, develop) Merge pull request #1 from Danon-1ch/feature/Danon-1ch-intro
|\
| * a986261 (origin/feature/Danon-1ch-intro, feature/Danon-1ch-intro) docs: add .env.example and .gitignore
| * fcdc239 docs: add NOTES.md
| * b54b056 docs: add ABOUT.md
* |   10c14ba Merge pull request #3 from Danon-1ch/hotfix/Danon-1ch-typo
|\ \
| |/
|/|
| | * 94a1816 (origin/main, origin/HEAD, main) Merge pull request #2 from Danon-1ch/hotfix/Danon-1ch-typo
| |/|
|/|/
| * 7d5056d (origin/hotfix/Danon-1ch-typo, hotfix/Danon-1ch-typo) fix: correct typo
| * a3669b1 feat: add hello.txt
|/
* d6ebc92 Initial commit
<img width="756" height="255" alt="graph" src="https://github.com/user-attachments/assets/4a82ec40-3b08-4c56-9ea0-9ec0fafad706" />

## 5. Таблица Git Flow

| Ветка | Откуда | Куда | Зачем |
|-------|--------|------|-------|
| main | — | release/*, hotfix/* | стабильный прод |
| develop | main | feature/*, release/* | интеграция фич |
| feature/* | develop | develop | одна фича |
| release/* | develop | main + develop | подготовка релиза |
| hotfix/* | main | main + develop | срочный фикс прода |

## 6. Объяснение

- **main vs develop:** main — код, который видят пользователи, всегда стабильный.
  develop — сюда сливаются все фичи, тут код «собирается» перед релизом.
- **release/*:** отдельная ветка для финального тестирования и бампов версии
  перед выкаткой в main.
- **hotfix/*:** срочная правка бага в проде. Ответвляется от main, мержится
  обратно в main И в develop, чтобы фикс не потерялся в следующем релизе.

## 7. Безопасность

- `.env` в remote отсутствует (`.env.example` есть).
- Конфликт слияния разрешён, маркеров `<<<<<<<`/`>>>>>>>` нет.
