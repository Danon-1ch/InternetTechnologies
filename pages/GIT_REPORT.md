# Отчёт по задаче TZ-TF-01 (Sprint 0)

**Студент:** Danon-1ch
**Репозиторий:** https://github.com/Danon-1ch/InternetTechnologies

## 1. Ветки в репозитории

$ git branch -a
* develop
  feature/Danon-1ch-hw1
  feature/Danon-1ch-intro
  hotfix/Danon-1ch-typo
  main

<img width="353" height="89" alt="branch" src="https://github.com/user-attachments/assets/3f172291-b445-4405-9b79-9639891b32b6" />

## 2. PR фичи

- **PR #1:** feature/Danon-1ch-intro → develop
- **PR #4:** feature/Danon-1ch-hw1 → develop
- **PR #5:** feature/Danon-1ch-hw1 → develop
- Ссылка: https://github.com/Danon-1ch/InternetTechnologies/pull/1 https://github.com/Danon-1ch/InternetTechnologies/pull/4 https://github.com/Danon-1ch/InternetTechnologies/pull/5
- Файлы: students/Danon-1ch/ABOUT.md, NOTES.md, .env.example, pages/GIT_REPORT.md, index.html, styles.css

## 3. Hotfix

- **PR #2:** hotfix/Danon-1ch-typo → main
- **PR #3:** hotfix/Danon-1ch-typo → develop
- Ссылки: https://github.com/Danon-1ch/InternetTechnologies/pull/2 https://github.com/Danon-1ch/InternetTechnologies/pull/3
- Правка: опечатка в sandbox/hello.txt (`wrold` → `world`)

## 4. Граф истории

$ git log --oneline --graph --all
*   6df9610 (HEAD -> develop, origin/develop) Merge pull request #5 from Danon-1ch/feature/Danon-1ch-hw1
|\
| * e0c769d (origin/feature/Danon-1ch-hw1, feature/Danon-1ch-hw1) chore: add root gitignore
* | aa1edbc Merge pull request #4 from Danon-1ch/feature/Danon-1ch-hw1
|\|
| * 6801e4a feat: add hw1 landing page, docs: add git flow report
|/
*   c18b1a3 Merge pull request #1 from Danon-1ch/feature/Danon-1ch-intro
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
<img width="743" height="341" alt="image" src="https://github.com/user-attachments/assets/56d96287-5ee3-4acb-8f29-2cb24e6193a9" />


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
