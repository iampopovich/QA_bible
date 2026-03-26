# План структуризации и актуализации раздела «Автоматизация»

Дата анализа: 2026-03-26
Статус: в работе

---

## Контекст

Раздел создавался ~2021–2022 году и с тех пор не обновлялся. Из 15 файлов 3 критически устарели, 8 требуют обновления, 4 приемлемы по базовой теории. Бета-статус де-факто означает заброшенный раздел.

Задачи:
- убрать пометку `(beta)` из названия раздела в SUMMARY.md
- привести все файлы к STYLE_GUIDE.md
- актуализировать технологический стек (2024–2025)
- закрыть критические пробелы новыми файлами

---

## Целевая структура раздела

```
Автоматизация тестирования (Automation Testing)
│
├── README.md                          — введение в раздел (переписать)
│
├── ОСНОВЫ
│   ├── obshee.md                      — что такое автоматизация, зачем, когда
│   ├── chto-nuzhno-avtomatizirovat.md — критерии выбора: что автоматизировать
│   └── luchshie-praktiki-avtomatizacii.md — принципы и антипаттерны
│
├── ИНСТРУМЕНТЫ И ФРЕЙМВОРКИ
│   ├── vidy-i-instrumenty-avtomatizacii.md  — обзор видов и сравнение фреймворков
│   ├── instrumenty-api-testirovaniya.md     — [НОВЫЙ] Bruno, Playwright API, REST Assured
│   └── vizualnoe-regressionnoe-testirovanie.md — [НОВЫЙ] Percy, Applitools, Playwright snapshots
│
├── CI/CD И ИНФРАСТРУКТУРА
│   ├── infrastruktura-i-paiplain-ci-cd.md   — GitHub Actions, GitLab CI, Jenkins, Docker
│   └── processy-i-avtomatizaciya-proekta-s-nulya.md — автоматизация с нуля: кейс + принципы
│
├── ТЕХНИКИ И ПАТТЕРНЫ
│   ├── parallelnoe-testirovanie-parallel-testing.md  — sharding, cloud execution, стратегии
│   ├── chto-takoe-flaky-tests.md                     — причины, диагностика, платформы
│   ├── mutacionnoe-testirovanie-mutation-testing.md  — теория + Stryker, PIT, mutmut
│   ├── podkozhnyi-test-subcutaneous-test.md          — subcutaneous тесты, Testing Library
│   └── raznica-mezhdu-coupling-i-cohesion.md         — coupling/cohesion (рассмотреть перенос)
│
├── КАРЬЕРА
│   └── kak-stat-avtomatizatorom-i-voprosy-s-sobesedovanii.md
│
└── РЕСУРСЫ
    ├── poleznye-ssylki.md  — актуальные ссылки по инструментам
    └── drugoe-ssylki.md    — актуализировать или влить в poleznye-ssylki
```

---

## Задачи по файлам

### Приоритет 1 — критично (содержат устаревшую/вводящую в заблуждение информацию)

#### `vidy-i-instrumenty-avtomatizacii.md`
- [ ] Удалить Protractor из всех рекомендаций (EOL август 2023, официально мёртв)
- [ ] Добавить Playwright как лидера рынка (45% adoption, 38M npm-загрузок/нед., обогнал Cypress)
- [ ] Обновить позицию Cypress: стабилен, но рост остановился, Playwright перехватил momentum
- [ ] Добавить Testcontainers (интеграционные тесты без моков — библиотека, не платформа)
- [ ] Добавить раздел «AI как инструмент инженера»: Percy SDK, Applitools Eyes SDK, Copilot для boilerplate — с акцентом на интеграцию через код, а не замену кода; low-code платформы упомянуть кратко с честной оценкой их потолка
- [ ] Обновить таблицу сравнения фреймворков
- [ ] Привести к STYLE_GUIDE: заменить `**bold**`-заголовки на `##`/`###`, добавить `## Источники`

#### `infrastruktura-i-paiplain-ci-cd.md`
- [ ] Добавить GitHub Actions как основной CI для новых проектов (68% проектов на GitHub)
- [ ] Добавить GitLab CI как enterprise-стандарт
- [ ] Переосмыслить позицию Jenkins: legacy backbone, не стандарт для новых проектов
- [ ] Добавить паттерн современного pipeline (unit → интеграция → E2E sharding → visual regression → contract tests)
- [ ] Добавить test sharding (нативно в Playwright, Vitest, Jest)
- [ ] Добавить раздел про flaky test quarantine в CI (BuildPulse, Currents)
- [ ] Привести к STYLE_GUIDE

#### `drugoe-ssylki.md`
- [ ] Заменить тренды 2021 года на актуальный контент или убрать датированные статьи
- [ ] Либо влить полезное содержимое в `poleznye-ssylki.md` и удалить файл
- [ ] Если оставить — переименовать с понятным названием темы

---

### Приоритет 2 — существенные пробелы

#### `parallelnoe-testirovanie-parallel-testing.md`
- [ ] Раскрыть тему: сейчас 19 строк на важную тему
- [ ] Добавить: natively sharding в Playwright (`--shard=1/4`), Vitest, Jest
- [ ] Добавить: стратегии параллелизации (по файлу, по тесту, по окружению)
- [ ] Добавить: cloud execution (BrowserStack Automate, Sauce Labs, LambdaTest)
- [ ] Добавить: проблемы параллельных тестов (shared state, race conditions, DB isolation)
- [ ] Привести к STYLE_GUIDE

#### `kak-stat-avtomatizatorom-i-voprosy-s-sobesedovanii.md`
- [ ] Обновить список ожидаемых технологий: добавить TypeScript, Playwright
- [ ] Добавить вопросы по CI/CD (GitHub Actions), контрактному тестированию
- [ ] Добавить блок про AI-инструменты как ожидаемое знание
- [ ] Убрать устаревшие вопросы по Protractor
- [ ] Привести к STYLE_GUIDE

#### `poleznye-ssylki.md`
- [ ] Проверить и удалить мёртвые ссылки
- [ ] Добавить: Playwright docs, k6 docs, Bruno, Maestro, Testcontainers
- [ ] Добавить: курсы 2023–2025 (Playwright, k6, GitHub Actions)
- [ ] Привести к STYLE_GUIDE

---

### Приоритет 3 — style guide и дополнения

#### `obshee.md`
- [ ] Структурировать: сейчас Q&A-блоки без нормальной heading hierarchy
- [ ] Заменить `**bold**`-заголовки на `##`/`###`
- [ ] Добавить `## Источники`
- [ ] Разбить длинные абзацы (>6 строк)

#### `luchshie-praktiki-avtomatizacii.md`
- [ ] Контент актуален — только style guide правка
- [ ] Заменить `**bold**`-заголовки на `##`/`###`
- [ ] Добавить `## Источники`

#### `chto-nuzhno-avtomatizirovat.md`
- [ ] Расширить: добавить современные соображения (PWA, accessibility automation)
- [ ] Структурировать: сейчас просто bulleted list без разделов
- [ ] Добавить `## Источники`

#### `mutacionnoe-testirovanie-mutation-testing.md`
- [ ] Добавить раздел с инструментами: Stryker (JS/TS), PIT (Java), mutmut (Python)
- [ ] Привести к STYLE_GUIDE

#### `processy-i-avtomatizaciya-proekta-s-nulya.md`
- [ ] Обновить стек в кейсе: заменить Jenkins на GitHub Actions как современный аналог, упомянуть оба
- [ ] Добавить современные альтернативы REST Assured и Cucumber
- [ ] Привести к STYLE_GUIDE

#### `podkozhnyi-test-subcutaneous-test.md`
- [ ] Актуализировать: упомянуть Vitest, Testing Library как современные инструменты
- [ ] Привести к STYLE_GUIDE

#### `chto-takoe-flaky-tests.md`
- [ ] Добавить раздел: платформы для отслеживания и карантина flaky-тестов (BuildPulse, Currents)
- [ ] Добавить: async/await паттерны как решение для веб (Playwright auto-waiting)
- [ ] Привести к STYLE_GUIDE

#### `raznica-mezhdu-coupling-i-cohesion.md`
- [ ] Оценить: тема скорее про архитектуру кода, не про автоматизацию тестирования
- [ ] Рассмотреть перенос в более подходящий раздел или оставить с пояснением контекста
- [ ] Привести к STYLE_GUIDE

---

### Новые файлы для создания

#### `instrumenty-api-testirovaniya.md` — [НОВЫЙ]
Содержание:
- Bruno (open-source, git-friendly, замена Postman)
- Hoppscotch (web-based, REST/GraphQL/WebSocket/gRPC)
- Playwright API testing (встроенный, без доп. инструментов)
- REST Assured (Java-стандарт)
- Postman (всё ещё популярен, но теряет аудиторию)
- Сравнительная таблица по критериям

#### `vizualnoe-regressionnoe-testirovanie.md` — [НОВЫЙ]
Содержание:
- Что такое visual regression testing и зачем
- Playwright built-in screenshots (`toHaveScreenshot`)
- Percy (BrowserStack) — cross-browser, AI Visual Review Agent
- Chromatic — компонентный уровень, Storybook-интеграция
- Applitools Eyes — AI visual AI, enterprise
- Сравнительная таблица

---

### README.md
- [ ] Убрать пометку `(beta)` или заменить на полноценное введение
- [ ] Написать 3–4 предложения: что такое автоматизация тестирования и что найдёт читатель в разделе
- [ ] Привести к STYLE_GUIDE

---

## Технологический стек: что актуально в 2025

### E2E веб-фреймворки
| Инструмент | Статус 2025 |
|---|---|
| **Playwright** | Лидер: 45% adoption, 38M npm/нед., обогнал Cypress |
| **Cypress** | Стабилен, рост остановился; силён в React-командах |
| **Selenium** | Legacy enterprise, 22% рынка; не стандарт для новых проектов |
| WebdriverIO | Нишевый; лучшая интеграция с Appium |
| Protractor | **Мёртв** — EOL август 2023. Убрать из рекомендаций |
| Puppeteer | Жив, но репозиционирован как dev-инструмент, не E2E-фреймворк |

### CI/CD
| Инструмент | Статус 2025 |
|---|---|
| **GitHub Actions** | Стандарт для новых проектов (68% GitHub-проектов) |
| **GitLab CI** | Enterprise-стандарт, встроен в платформу |
| Jenkins | Legacy backbone; 67% команд мигрируют от него |
| Azure DevOps | 24% рынка, Microsoft-экосистема |
| CircleCI / TeamCity | Нишевые enterprise |

### Мобильная автоматизация
| Инструмент | Статус 2025 |
|---|---|
| **Appium 2.x** | Стандарт cross-platform; WebdriverIO — лучший клиент |
| **Maestro** | Новый фаворит для smoke/sanity (YAML, прост, кросс-платформа) |
| **Detox** | Лучший для React Native |
| XCUITest | Нативный iOS, самый быстрый |
| Espresso | Нативный Android, самый быстрый |

### API-тестирование
| Инструмент | Статус 2025 |
|---|---|
| **Bruno** | Breakout: open-source, git-friendly, замена Postman |
| **Playwright API** | Встроен в Playwright, без доп. зависимостей |
| **REST Assured** | Java-стандарт |
| Postman | Всё ещё лидер (22%), но теряет аудиторию из-за pricing |
| Hoppscotch | Лёгкая open-source альтернатива |

### Performance testing
| Инструмент | Статус 2025 |
|---|---|
| **k6 (Grafana)** | Стандарт для DevOps-команд; JS, низкое потребление ресурсов |
| **JMeter** | Legacy enterprise; сложные протоколы (JDBC, LDAP, JMS) |
| Gatling | Растёт в enterprise (code-first, хорошие отчёты) |
| Locust | Python-экосистема |
| Artillery | Cloud-native фокус |

### AI как инструмент инженера (не замена инженеру)

Акцент — не на low-code/no-code платформах, а на том, как AI усиливает инженера, который понимает что делает.

| Инструмент | Как усиливает инженера |
|---|---|
| **GitHub Copilot / Claude / GPT** | Ускоряет написание boilerplate, page objects, фикстур — но результат требует ревью и рефакторинга |
| **Applitools Eyes SDK** | Библиотека, интегрируется в Playwright/Cypress/Selenium кодом — не платформа-замена |
| **Percy SDK** | То же: npm/pip пакет, вызывается из тестового кода, не заменяет фреймворк |
| **Testcontainers** | Библиотека для Java/Go/Python/Node — пишешь код, получаешь реальные БД/брокеры в тестах |
| **Launchable / BuildPulse** | Интеграции к существующему CI, анализируют junit-xml — не переписывают тесты |

Low-code платформы (Mabl, Testim, TestRigor) — упомянуть как существующий класс инструментов с честной оценкой потолка: сложная бизнес-логика, data-driven тесты, нестандартные flow требуют кода. Не рекомендовать как основной путь развития.

---

## Языки программирования в автоматизации: тренды 2024–2025

### Расстановка сил по данным опросов

| Язык | Доля среди тестировщиков | Тренд | Источник |
|---|---|---|---|
| **TypeScript** | 35% всех разработчиков | Рост с 12% (2017) → лидер | JetBrains DevEcosystem 2024 |
| **Python** | 34% тестировщиков | Уверенный рост | JetBrains DevEcosystem 2023 (тест-секция) |
| **Java** | 32% тестировщиков / 43% enterprise | Стагнация; снижение с 54% (2020) | JetBrains 2024, Applitools Survey |
| **JavaScript** | 37% тестировщиков (JS+TS вместе) | Медленно уступает TypeScript | JetBrains 2023 (тест-секция) |
| **Kotlin** | >90% топ-1000 Google Play | Уверенный рост в Android | Google/Android официальные данные |
| **Go** | ~4 млн профессионалов | Рост, особенно в DevOps/infra | JetBrains Go Report 2025 |

**Итоговый рейтинг языков по привлекательности** (JetBrains Language Promise Index 2024):
`TypeScript → Rust → Python → Go → Java`

### TypeScript: почему обогнал всех в автоматизации

В августе 2025 TypeScript впервые стал языком **#1 на GitHub** по числу репозиториев, обогнав JavaScript и Python (GitHub Octoverse 2025). В Playwright-репозиториях 91% кода написан на TypeScript (анализ 424 000+ репо, TestDino).

Структурные причины роста:
- Playwright написан на TypeScript, TypeScript-режим рекомендуется по умолчанию
- Cypress добавил TypeScript как first-class в v10 (2022)
- Статическая типизация ловит ошибки в Page Object Models до runtime — критично для больших test suite
- Angular/Next.js/NestJS скаффолдируются с TypeScript → QA переходит на тот же язык
- GitHub Copilot генерирует более точный код для типизированных языков — дополнительный драйвер 2024–2025

### Python: рост за счёт pytest и AI-волны

- pytest стал стандартом де-факто: 1300+ плагинов, используется Amazon, Apple, IBM, Intel
- Playwright официально поддерживает Python как один из четырёх языков
- Количество запросов «Selenium Python» в Stack Overflow Trends 2024 впервые обогнало «Selenium Java»
- AI/ML-тестирование (TensorFlow, PyTorch) требует Python → QA-специалисты в ML-командах пишут на Python

### Java: живёт там, где уже работает

Java не умирает, но теряет новые проекты. Остаётся стандартом в:
- Enterprise (банки, страхование, ритейл-гиганты) — существующая кодовая база, дорогой рефакторинг
- Backend интеграционное тестирование (Spring Boot + WireMock + REST Assured + TestNG)
- Android legacy (Espresso-тесты исторически на Java, сейчас Kotlin вытесняет)

ThoughtWorks Tech Radar классифицировал Selenium (основной инструмент Java-тестировщиков) как **Hold** для новых проектов.

### Kotlin и Swift: нативные языки платформ

**Kotlin (Android):**
- Google официально рекомендует Kotlin как основной язык Android
- >70% вакансий Android-разработчиков требуют Kotlin
- Espresso-примеры в официальной документации Google — на Kotlin
- Kotlin-корутины нативно работают в async UI-тестах

**Swift (iOS):**
- На WWDC 2024 Apple представила **Swift Testing** — официальная замена XCTest для unit-тестов
- Макросы `@Test` и `#expect` вместо наследования от `XCTestCase`
- Параллельное выполнение тестов по умолчанию
- XCUITest остаётся для UI-тестов; Swift Testing и XCTest сосуществуют в одном проекте

### Что отражать в файлах раздела

- `kak-stat-avtomatizatorom`: добавить TypeScript как базовый ожидаемый язык, обновить Java/Python секции
- `vidy-i-instrumenty-avtomatizacii`: обновить примеры кода с учётом TypeScript/Kotlin
- Новый файл `yazyki-v-avtomatizacii.md` — рассмотреть как отдельную статью с таблицами и обоснованием выбора

---

## Мобильное тестирование: актуальный ландшафт 2025

### Инструменты по уровням

| Уровень | Android | iOS | Cross-platform |
|---|---|---|---|
| Unit / компонент | **Espresso**, JUnit | **XCUITest**, Swift Testing | — |
| Smoke / sanity E2E | Espresso / **Maestro** | XCUITest / **Maestro** | **Maestro** |
| Сложные E2E | Espresso | XCUITest / EarlGrey 2.0 | **Appium 2.x** (WebdriverIO-клиент) |
| React Native | Detox / Maestro | Detox / Maestro | **Detox** (глубокий), **Maestro** (простой) |
| Flutter | integration_test | integration_test | integration_test + Maestro |

### Maestro — главный новичок рынка

Maestro (mobile.dev, 2022) — самый быстрорастущий инструмент мобильного тестирования:
- 13 100+ GitHub stars, Apache-2.0 лицензия
- YAML-синтаксис, не требует изменений в приложении (black-box)
- Кросс-платформа: iOS, Android, React Native, Flutter, Web
- Flakiness < 1% в сравнении с < 2% у Detox и нестабильностью Appium
- Todoist: миграция 63 тестов с Appium → pass rate с 50% до 99%+, время с 80 до 20 минут
- Maestro Studio (визуальный редактор) + Maestro Cloud (параллельное выполнение)

**Рекомендация 2025:** Maestro — первый выбор для smoke/sanity, особенно для кросс-платформных команд и QA без опыта написания кода.

### Appium: статус и версии

- **Appium 1.x — EOL**, документация не ведётся
- **Appium 2.x** — production standard 2023–2024, plugin-архитектура
- **Appium 3.0** вышел в августе 2025:
  - Минимальный Node.js 20.19+
  - Полное удаление JSONWP — только W3C WebDriver
  - Все крупные облачные платформы (BrowserStack, Sauce Labs) требуют 2.x+

### Detox vs Maestro: выбор для React Native

| Критерий | Detox | Maestro |
|---|---|---|
| Архитектура | Gray-box, в-процессе | Black-box, accessibility layer |
| Язык тестов | TypeScript/JavaScript | YAML |
| Сложность настройки | Высокая (native build hooks) | Очень низкая |
| Flakiness | < 2% | < 1% |
| Мокирование API | Да | Ограничено |
| Системные диалоги | Ограничено | Лучше |
| Выбор 2025 | Программный контроль, мокирование | Простота, скорость онбординга |

### Облачные фермы устройств

| Платформа | Реальные устройства | Доля рынка | Особенность |
|---|---|---|---|
| **BrowserStack** | 20 000+ | ~31% | Широчайший охват; Percy visual testing |
| **LambdaTest** | Большой парк | Быстро растёт | Лучшее соотношение цена/качество, KaneAI |
| **Sauce Labs** | 7 500+ | Enterprise лидер | SOC2/ISO 27001, сложные DevOps-интеграции |
| **Firebase Test Lab** | Real + virtual | — | Лучший для Android/Google Play; бесплатный tier |
| **AWS Device Farm** | Ограничен | ~3.7% | AWS-native инфраструктура |

**Ключевой факт:** 34% мобильных production-багов воспроизводятся только на конкретных физических устройствах, не на эмуляторах (SmartBear 2024) — обосновывает необходимость cloud-ферм.

### Flutter: flutter_driver устарел

`flutter_driver` официально deprecate, путь миграции — `integration_test`:
- Тесты и приложение собираются в единый APK/IPA
- Нативно работает с Firebase Test Lab
- Та же API, что и widget-тестирование → меньше порог входа
- Для black-box E2E: Maestro поддерживает Flutter без изменений в коде

### Что отражать в файлах раздела

- `vidy-i-instrumenty-avtomatizacii.md`: обновить мобильную секцию, добавить Maestro, Appium 3.0, flutter_driver → integration_test
- Создать новый файл `mobilnaya-avtomatizaciya.md` или дать ссылку на раздел `mobilnoe-testirovanie/`

---

## AI-решения вендоров для тестирования: состояние 2025

В 2024–2025 годах произошёл массовый сдвиг: крупные платформенные вендоры встроили AI-помощники непосредственно в инструменты разработки, а не только продают их как отдельные продукты.

### Что умеют вендорские AI-инструменты

| Вендор / Продукт | Что делает | GA с | Реальные ограничения |
|---|---|---|---|
| **GitHub Copilot** | Генерация unit-тестов в IDE (`/tests`), анализ покрытия | 2023 | Без существующего test suite: 7% рабочих тестов; с suite: ~45% (AST 2024) |
| **Azure DevOps MCP** | Copilot работает с test plans через MCP Server | Окт 2025 | Требует MCP-интеграции, не автономен |
| **Google Android Studio (Journeys)** | Описание сценариев на естественном языке → Gemini выполняет UI-тест в эмуляторе | 2024 | Только Android Studio + эмулятор |
| **Firebase App Testing Agent** | Автономный тест-агент для мобильных приложений | 2024 | Только мобильные приложения |
| **Amazon Q Developer** | Генерация тестов, review кода (переименован из CodeWhisperer в апр 2024) | 2024 | Фокус на AWS-стек |
| **JetBrains AI Assistant** | Генерация тестов в контексте метода/класса | 2024 | Только уровень метода, не весь модуль |
| **Atlassian Rovo** | Генерация тест-кейсов из user stories в Jira | Апр 2025 (Premium+) | Требует Xray для полной связки |
| **Salesforce Agentforce** | Генерация Apex-тестов с соблюдением org-специфичных правил | Сент 2024 | Только Apex/LWC стек |
| **Apple Xcode 26** | Открыл API для ChatGPT/Claude/локальных моделей | 2025 | Apple не создала свою LLM |
| **BrowserStack Percy** | AI Visual Review Agent: фильтрует 40% ложных срабатываний, ускоряет ревью в 3x | 2024 | Только visual regression |
| **Tricentis Agentic TA** | AI-агент: заявлено 85% снижение ручных усилий при создании тестов | 2025 | Нет независимых бенчмарков |
| **Katalon TrueTest** | Анализирует поведение реальных пользователей → генерирует regression по популярным user journeys | 2025 | SaaS, требует доступа к production трафику |
| **TestRail AI Test Case Generation** | Генерация тест-кейсов, human-in-the-loop | 2025 | Появился поздно, акцент на ручном контроле |

### Общий консенсус индустрии

Позитивный sentiment к AI-инструментам тестирования **упал с 70%+ (2023) до 60% (2025)** — эйфория сменяется реализмом. 65–70% организаций остаются в стадии pilot/PoC.

**Где AI работает хорошо:**
- Self-healing locators (Testim, Mabl) — снижают maintenance cost
- Visual regression с фильтрацией шума (Percy, Applitools) — зрелые решения
- Генерация unit-тест boilerplate — ускоряет написание, но требует ревью
- Анализ crash-репортов и failure classification

**Где AI пока слаб:**
- Сложная бизнес-логика и граничные условия — AI не понимает бизнес-контекст
- Edge cases — нужна экспертиза человека
- Многофайловый контекст — AI теряет связность при сложных зависимостях
- E2E-тесты с нестандартными flow — генерирует happy path, пропускает негативные сценарии

### Что это значит для QA-специалистов

Ключевой тезис: **AI усиливает инженера с навыками, но не заменяет необходимость их иметь.** Специалист, не понимающий что происходит в коде, не сможет оценить качество сгенерированного теста — он не увидит, что Copilot написал тест, который всегда проходит, или пропустил граничное условие.

Правильный фокус развития — не освоение low-code платформ, а:
- Глубокое понимание одного code-first фреймворка (Playwright + TypeScript / pytest + Python / Espresso + Kotlin)
- Знание архитектурных паттернов тестового кода: Page Object, Builder, Fixture, Factory
- Понимание CI/CD на уровне написания pipeline-конфигов, а не только нажатия кнопки
- Умение читать и отлаживать код приложения — не только тесты

AI-инструменты вендоров в этом контексте — ускоритель рутины: генерация boilerplate, подсказки по API, первый вариант теста для ревью. Навык prompt engineering для тестирования (как сформулировать задачу AI-ассистенту) — полезная компетенция, но вторичная относительно инженерной базы.

Статистика: 77% организаций инвестируют в AI-тестирование (World Quality Report 2024), при этом 42% тестировщиков по-прежнему не чувствуют себя уверенно в написании автоматизации (State of Testing 2024) — разрыв навыков никуда не делся.

### Что отражать в файлах раздела

- `vidy-i-instrumenty-avtomatizacii.md`: добавить подраздел «AI-инструменты автоматизации» с таблицей
- `kak-stat-avtomatizatorom.md`: добавить знание AI-инструментов как ожидаемую компетенцию
- Дать ссылку на раздел `ai-v-testirovanii/` для детального разбора

---

## Что добавить в SUMMARY.md после реструктуризации

Текущая структура плоская. После работ — сгруппировать по блокам через именованные группы или порядок файлов:

```
* [Автоматизация тестирования](avtomatizaciya-beta/README.md)
  * [Общее](avtomatizaciya-beta/obshee.md)
  * [Что автоматизировать](avtomatizaciya-beta/chto-nuzhno-avtomatizirovat.md)
  * [Виды и инструменты автоматизации](avtomatizaciya-beta/vidy-i-instrumenty-avtomatizacii.md)
  * [Инструменты API-тестирования](avtomatizaciya-beta/instrumenty-api-testirovaniya.md)
  * [Визуальное регрессионное тестирование](avtomatizaciya-beta/vizualnoe-regressionnoe-testirovanie.md)
  * [Инфраструктура и пайплайн (CI/CD)](avtomatizaciya-beta/infrastruktura-i-paiplain-ci-cd.md)
  * [Процессы и автоматизация проекта с нуля](avtomatizaciya-beta/processy-i-avtomatizaciya-proekta-s-nulya.md)
  * [Лучшие практики автоматизации](avtomatizaciya-beta/luchshie-praktiki-avtomatizacii.md)
  * [Параллельное тестирование](avtomatizaciya-beta/parallelnoe-testirovanie-parallel-testing.md)
  * [Flaky tests](avtomatizaciya-beta/chto-takoe-flaky-tests.md)
  * [Мутационное тестирование](avtomatizaciya-beta/mutacionnoe-testirovanie-mutation-testing.md)
  * [Подкожный тест (Subcutaneous test)](avtomatizaciya-beta/podkozhnyi-test-subcutaneous-test.md)
  * [Coupling и Cohesion](avtomatizaciya-beta/raznica-mezhdu-coupling-i-cohesion.md)
  * [Как стать автоматизатором и вопросы с собеседований](avtomatizaciya-beta/kak-stat-avtomatizatorom-i-voprosy-s-sobesedovanii.md)
  * [Полезные ссылки](avtomatizaciya-beta/poleznye-ssylki.md)
  * [Другое (ссылки)](avtomatizaciya-beta/drugoe-ssylki.md)
```
