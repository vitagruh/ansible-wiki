# Оглавление и план генерации вики

**Тема:** Ansible в администрировании и кибербезопасности
**Версия:** 0.1 (чертёж)
**Дата:** 2026-11-11
**Статус:** генерация запущена; ниже — утверждённая структура и порядок выпуска страниц.

## 1. Зафиксированные параметры

| Параметр | Значение |
|---|---|
| Среда | распределённая филиальная сеть; 200–1000 управляемых хостов; все ВМ на собственных хостах VMware ESXi |
| Виртуализация | vCenter и/или standalone ESXi (топология уточняется) |
| ОС | RHEL/Rocky/AlmaLinux 8–9, Ubuntu 22.04/24.04, Debian 12 |
| Платформы | сетевые устройства, Kubernetes on-prem; публичные облака — опционально |
| Исключено из базовой поставки | Windows Server/AD (добавляется отдельной страницей по запросу) |
| Baseline | ansible-core 2.17+; control node Python 3.10–3.12; managed nodes Python 3.7–3.12 (на RHEL 8 — python39) |
| Комплаенс | CIS Benchmarks (Linux, ESXi), DISA STIG (RHEL/Ubuntu), ISO/IEC 27001, NIST CSF 2.0, национальные/отраслевые требования |
| Стек | ansible-core + Git + CI + lint/Molecule → AWX/Semaphore → AAP при необходимости |
| Формат | MkDocs Material, многофайловый Markdown |
| Язык | русский; код и имена задач — английский |
| Объём | 800–2500 слов на страницу; всего ~95–130 тыс. слов |

## 2. Допущения (Проход 0)

Эти допущения не блокируют первые партии; по мере уточнения они заменяются фактами.

1. Число филиалов — 10–50; в среднем 10–30 хостов на филиал. Уточнить.
2. vCenter: как минимум один в ЦОД; в филиалах возможны standalone ESXi. Без vCenter часть операций с шаблонами и клонированием ограничена.
3. Юрисдикция и конкретные национальные/отраслевые требования не указаны; в тексте — плейсхолдеры и нейтральные формулировки.
4. SIEM/EDR не выбраны; интеграции описываются нейтрально (Wazuh/ELK/Splunk как примеры).
5. CI-платформа по умолчанию — GitLab CE (self-hosted); альтернатива — GitHub Actions.
6. Kubernetes: дистрибутив не указан; примеры — переносимые (kubeadm/RKE2), без привязки к OpenShift.
7. Вендоры сетевого оборудования не указаны; примеры — на уровне connection-плагинов и общих практик.
8. Публичные облака — опциональное расширение, не ядро вики.
9. Минорные версии ОС и ESXi уточняются; все команды проверяются на RHEL 9, Ubuntu 24.04, Debian 12.
10. Windows/AD исключены; при необходимости добавляются страницы `appendix/windows-ad.md`.

## 3. Принципы вики

1. **Defensive-only.** Только защитные практики: харденинг, контроль, обнаружение, реагирование, комплаенс.
2. **Запускаемость.** Примеры полные, с FQCN, `validate`, идемпотентностью и проверкой результата.
3. **Версионность.** Указывается baseline и различия между версиями; deprecated-модули не используются.
4. **Ограничение blast radius.** Для рискованных изменений — check/diff, canary, `serial`, откат.
5. **Без выдуманных сущностей.** Модули, параметры, флаги и URL проверяются по официальной документации.
6. **Связность.** Единая терминология, перекрёстные ссылки, навигация.
7. **Практичность.** Каждая страница заканчивается проверками и чек-листом, а не теорией.

## 4. Маршруты чтения

| Роль | Маршрут | Ориентир |
|---|---|---|
| Системный администратор | quickstart → fundamentals 01–09 → admin 20–24 → quality 50–52 → ops 60–62 | 2–3 недели |
| SecOps / SOC | fundamentals 01–05 → secure-dev 10–16 → security 35–48 → quality 51 → ops 61 | 3–4 недели |
| Архитектор | fundamentals 02 → secure-dev 10, 15 → admin 20, 24, 30 → security 40, 44, 47 → quality 53, 54 → ops 63 | 5–7 дней выборочно |
| Руководитель ИБ | index → secure-dev 10 → security 44, 45 → quality 54 → ops 63 | 1–2 дня выборочно |

## 5. Полное оглавление

Формат строки: `файл` — **название** · уровень · объём · содержание · связи.

### docs/index.md — **Главная страница вики** · basic · 600–900

Назначение, аудитория, статус публикации, маршруты чтения, обзор разделов, конвенции, ссылка на глоссарий.

### docs/start/

- `reading-paths.md` — **Маршруты чтения** · basic · 800–1200 · четыре роли, предпосылки, время, порядок страниц · → index, quickstart, glossary.
- `quickstart.md` — **Быстрый старт: первый безопасный playbook** · basic · 1500–2000 · установка ansible-core, SSH-ключи, inventory, ping, первый hardening-playbook через check/diff, проверка, откат · → 03, 04, 05, 09, 13.
- `glossary.md` — **Глоссарий** · basic · 2500–3500 · 80+ терминов по шести категориям · → все разделы.

### docs/fundamentals/

- `01-concepts.md` — **Основы Ansible** · basic · 1500–2000 · agentless, push-модель, декларативность, идемпотентность, жизненный цикл выполнения, когда Ansible не нужен · → 02, 07, 09.
- `02-architecture.md` — **Архитектура и компоненты** · basic/intermediate · 1800–2500 · control node, managed nodes, connection/inventory/module plugins, collections, EE, AAP/AWX; схема и trust boundaries · → 03, 10, 24, 53.
- `03-install.md` — **Установка и версионирование** · basic · 1500–2200 · ansible-core vs ansible package, pipx/venv, RHEL subscription, Python 3.10–3.12 на control node, Python 3.7+ на managed nodes, RHEL 8 python39, пиннинг и обновления · → 04, 15, 50.
- `04-config.md` — **Конфигурация ansible.cfg** · intermediate · 1500–2000 · приоритеты конфигурации, переменные окружения, безопасные значения host_key_checking/pipelining/become/log_path, каталоги inventory и collections · → 05, 12, 16.
- `05-inventory.md` — **Inventory и группы** · basic/intermediate · 1500–2200 · INI/YAML, children, паттерны, динамические плагины, иерархия филиалов, group_vars/host_vars, отделение секретов · → 06, 20, 30.
- `06-variables.md` — **Переменные, факты и приоритеты** · intermediate · 1800–2400 · 22 уровня приоритета, facts, magic variables, extra_vars, vault-переменные, именование, отладка · → 05, 11, 13.
- `07-playbooks-roles.md` — **Playbooks, roles, handlers** · intermediate · 2000–2800 · play/task, handlers и notify, include/import, структура роли, collections, tags, blocks, обработка ошибок, serial · → 01, 13, 50.
- `08-templates-lookups.md` — **Jinja2 и lookup-плагины** · intermediate · 1500–2200 · шаблоны, фильтры, tests, validate, lookup (env/file/vault), риски утечек и инъекций · → 06, 11, 13.
- `09-modules.md` — **Модули и FQCN** · basic/intermediate · 1500–2200 · выбор модуля, идемпотентность, check mode, shell/command и правила их применения, changed_when, возвращаемые значения · → 07, 13, 21.

### docs/secure-dev/

- `10-threat-model.md` — **Модель угроз автоматизации** · advanced · 2000–2800 · control node как tier-0, компрометация раннера, отравленный inventory, вредоносные коллекции, инъекции в шаблонах, утечки секретов; STRIDE, контроли, остаточный риск · → 02, 11, 12, 14, 15.
- `11-secrets.md` — **Управление секретами** · intermediate/advanced · 2200–3000 · ansible-vault, vault IDs, password file, HashiCorp Vault, SOPS, AWS/Azure, AAP credentials, ротация, no_log; таблица сравнения и примеры · → 06, 10, 12, 14, 53.
- `12-access.md` — **Доступ и привилегии** · intermediate · 1800–2400 · SSH-ключи и ротация, authorized_key exclusive, host key checking, bastion/ProxyJump, become/sudo, sudoers validate, сервисные учётки, RBAC, break-glass · → 10, 11, 25, 47.
- `13-safe-code.md` — **Безопасная разработка playbook** · intermediate · 2000–2800 · идемпотентность, check/diff, validate, block/rescue, changed_when, handlers, canary, rollback, blast radius, чек-лист ревью · → 07, 09, 50, 52.
- `14-cicd-secrets.md` — **Секреты в CI/CD** · intermediate · 1600–2200 · GitLab CE/GitHub Actions, защищённые ветки, OIDC, masked variables, защита раннеров, интеграция с Vault, логи · → 10, 11, 15, 51.
- `15-supply-chain.md` — **Безопасность цепочки поставок** · advanced · 1800–2400 · requirements.yml с пинами, приватный Galaxy/Hub, подпись коллекций и EE, SBOM, ревью зависимостей, офлайн-зеркала · → 03, 14, 48, 53.
- `16-audit-logging.md` — **Аудит выполнения** · intermediate · 1500–2000 · callback-плагины, log_path, JSON-логи, отправка в SIEM, ограничения no_log, аудит AWX/AAP, хранение и защита от изменения · → 14, 42, 53, 60.

### docs/admin/

- `20-branch-fleet.md` — **Распределённые филиалы** · intermediate/advanced · 2200–3000 · иерархия inventory, WAN-задержки и обрывы, таймауты/retries, центральный control node vs локальные execution nodes vs ansible-pull, расписания, throttle, офлайн-кэши, локальные журналы, maintenance windows; таблица сравнения · → 05, 12, 25, 30, 42, 53.
- `21-os-management.md` — **Управление Linux** · basic/intermediate · 2000–2800 · пакеты и репозитории (dnf/apt), GPG, пиннинг, пользователи и группы, SSH-ключи, cron/systemd timers, сервисы, NTP, limits; различия RHEL/Ubuntu/Debian · → 09, 22, 36.
- `22-config-drift.md` — **Конфигурация и дрейф** · intermediate · 1600–2200 · desired state, check mode, периодические прогоны, отчёты о дрейфе, исключения, ремедиация vs алертинг, validate конфигов · → 13, 21, 42, 44.
- `23-files-acl-selinux.md` — **Файлы, ACL, SELinux/AppArmor** · intermediate · 1600–2200 · права и владельцы, ACL, контексты и booleans SELinux, AppArmor, диагностика отказов, запрет chmod 777 · → 21, 35, 60.
- `24-vmware-esxi.md` — **VMware ESXi и vCenter** · intermediate/advanced · 2200–3000 · community.vmware, различия vCenter/standalone, жизненный цикл ВМ, шаблоны, снапшоты, теги, datastore, настройки хостов, NTP/syslog, резервное копирование конфигурации, least privilege API; схема · → 02, 29, 30, 40.
- `25-network-basics.md` — **Базовая сеть хоста** · basic · 1500–2000 · интерфейсы, маршруты, DNS, NTP, bonding, VLAN, VPN/SD-WAN, проверка и защита от потери управления · → 12, 20, 26, 37.
- `26-network-devices.md` — **Сетевые устройства** · intermediate · 1800–2400 · network_cli, вендорские коллекции, бэкап конфигураций, сравнение с baseline, массовые изменения с serial и откатом, AAA · → 25, 41, 60.
- `27-cloud.md` — **Публичные облака (опционально)** · intermediate · 1200–1600 · IAM-базлайны, тегирование, guardrails, обзор коллекций AWS/Azure; границы применимости · → 15, 41, 47.
- `28-containers-k8s.md` — **Kubernetes и контейнеры** · intermediate · 1800–2400 · kubernetes.core, аутентификация, RBAC, сетевые политики, kube-bench/CIS, Helm, секреты · → 11, 41, 47.
- `29-backup-dr.md` — **Резервное копирование и DR** · intermediate · 1500–2000 · расписания, консистентность, шифрование, offsite, проверка восстановления, RTO/RPO, роль снапшотов VMware · → 24, 44, 45.
- `30-scaling.md` — **Масштабирование и производительность** · intermediate/advanced · 1800–2400 · forks, serial, strategy, pipelining, fact caching, async, большие inventory, ресурсы control node для 200–1000 хостов, шардирование по филиалам, метрики · → 05, 20, 24, 53.
- `31-migration.md` — **Миграция и наследие** · intermediate · 1500–2200 · переход с 2.9 на ansible-core/collections, deprecated-модули, изменения Python, рефакторинг ролей, параллельный запуск, откат · → 03, 07, 09.

### docs/security/

- `35-linux-hardening.md` — **Харденинг Linux** · intermediate/advanced · 2500–3500 · CIS L1/L2, STIG CAT, dev-sec, ansible-lockdown, OpenSCAP, минимизация сервисов, обновления, исключения, доказательства; различия RHEL/Ubuntu/Debian · → 21, 36–38, 44.
- `36-auth-ssh-pam.md` — **SSH, PAM, sudo, MFA** · intermediate · 2200–3000 · таблица параметров sshd, validate, отключение root/паролей, AllowGroups, KEX/ciphers/MAC, faillock, pwquality, аудит sudo, MFA, защита от самоблокировки · → 12, 35, 37, 45.
- `37-firewall.md` — **Межсетевой экран** · intermediate · 1800–2400 · default-deny, nftables/firewalld/ufw, порядок правил, таймер отката, out-of-band доступ, филиальная периферия, проверка · → 25, 36, 45.
- `38-kernel-audit.md` — **Ядро и системный аудит** · advanced · 2000–2800 · sysctl baseline, auditd (execve, identity, привилегии), immutable, AIDE, целостность, защита журналов, влияние на производительность · → 35, 42, 45.
- `39-tls-pki.md` — **TLS и PKI** · intermediate · 1800–2400 · внутренний CA, ключи/CSR/сертификаты, распространение, продление, отзыв, проверка, ACME, хранение ключей · → 11, 36, 40, 45.
- `40-vmware-hardening.md` — **Харденинг ESXi/vCenter** · advanced · 2200–3000 · доступ и lockdown, отключение SSH, сервисные учётки и RBAC, сертификаты, NTP, syslog, vDS, снапшоты, шифрование, CIS VMware/Hardening Guide, бэкап конфигурации · → 24, 39, 42, 44.
- `41-network-cloud-hardening.md` — **Сеть и облако** · intermediate · 1800–2400 · AAA на устройствах, baseline конфигов, SCP/Azure Policy, CSPM, сегментация, VPN/SD-WAN, least privilege · → 26, 27, 37, 47.
- `42-logging-monitoring.md` — **Логирование и мониторинг** · intermediate · 1800–2400 · journald/rsyslog, TLS, агенты SIEM/EDR, буферизация при обрывах WAN, полнота покрытия, парсинг, хранение, защита от изменения · → 16, 38, 45, 46.
- `43-vuln-patching.md` — **Уязвимости и патчи** · intermediate/advanced · 2000–2800 · CVE/CVSS, SLA, приоритизация, экстренное закрытие через Ansible, верификация устранения, повторный скан, откат, исключения · → 35, 44, 46.
- `44-compliance.md` — **Комплаенс и доказательства** · intermediate · 2200–3000 · маппинг контроль → playbook → доказательство, CIS/STIG/ISO/NIST и нац. требования, отчёты, хранение, жизненный цикл исключений, аудиторский след, метрики · → 22, 35–43, 61.
- `45-incident-response.md` — **Реагирование на инциденты** · advanced · 2200–3000 · изоляция с предохранителями, сбор артефактов, хэши, chain of custody, восстановление, пост-инцидентный харденинг, учения · → 37, 42, 46, 47.
- `46-eda.md` — **Event-Driven Ansible** · advanced · 1600–2200 · ansible-rulebook/ansible.eda, источники событий, условия, троттлинг, апрувы, kill switch, dry-run, WAN, интеграция с SIEM · → 42, 43, 45, 53.
- `47-zero-trust.md` — **Zero trust и JIT-доступ** · advanced · 1600–2200 · JIT, автоматическое истечение прав, bastion и session recording, PAM, mTLS, депровижининг, сегментация филиалов, VPN/SD-WAN · → 12, 25, 41, 45.
- `48-airgap.md` — **Air-gapped среды** · intermediate · 1500–2000 · зеркала, офлайн-коллекции и EE, подписанные бандлы, регламент переноса, частота обновлений, проверка целостности, ansible-pull · → 15, 20, 53.

### docs/quality/

- `50-testing.md` — **Тестирование автоматизации** · intermediate · 2000–2800 · yamllint, ansible-lint production, Molecule, проверка идемпотентности, testinfra, эфемерная инфраструктура, матрица ОС, тесты ролей · → 07, 13, 51.
- `51-cicd-gitops.md` — **CI/CD и GitOps** · intermediate · 1800–2400 · этапы пайплайна, защищённые ветки, OIDC, окружения, апрувы, canary через serial, GitOps-модель · → 14, 50, 52, 53.
- `52-review-release.md` — **Ревью и релизы** · intermediate · 1500–2000 · чек-лист PR, security review, семантическое версионирование, CHANGELOG, deprecation, подпись релизов · → 13, 15, 51, 54.
- `53-aap-awx.md` — **AAP, AWX, Semaphore** · intermediate/advanced · 2200–3000 · сравнение, компоненты, RBAC, credentials, projects, workflows, approval nodes, mesh, HA, аудит, sizing для 200–1000 хостов, рекомендация по этапам · → 14, 15, 20, 30, 51, 54.
- `54-governance.md` — **Governance и процессы** · intermediate · 1800–2400 · RACI, именование, структура репозиториев, change management, метрики, документация, владельцы, исключения · → 44, 52, 53, 63.
- `55-training-lab.md` — **Обучение и лаборатория** · basic · 1200–1800 · варианты лаборатории, учебные сценарии, план обучения, сертификации, внутренние воркшопы · → quickstart, 50, 63.

### docs/ops/

- `60-troubleshooting.md` — **Диагностика и troubleshooting** · intermediate · 2200–3000 · деревья решений и таблицы симптом → причина → проверка → решение: SSH, become, Python, SELinux, WAN, ESXi API, сетевые устройства, ansible-pull; verbosity, debugger, callback · → все технические разделы.
- `61-checklists.md` — **Чек-листы** · basic · 1800–2400 · внедрение, харденинг, релиз playbook, инцидент, air-gapped обновление, подключение филиала, изменение VMware · → 44, 45, 52, 63.
- `62-antipatterns.md` — **Анти-паттерны** · intermediate · 1600–2200 · пары «плохо/хорошо»: shell вместо модуля, отсутствие changed_when, секреты в логах, ignore_errors, глобальный become, непроверенные роли, отсутствие serial и отката · → 13, 50, 60.
- `63-roadmap.md` — **Дорожная карта внедрения** · basic · 1500–2000 · 30/90/180 дней, этапы, KPI, риски, роли команды · → 53, 54, 61.
- `64-faq.md` — **FAQ** · basic · 2000–2800 · 30+ вопросов по выбору стека, филиалам, VMware, секретам, тестированию, комплаенсу · → все разделы.
- `65-cheatsheet.md` — **Шпаргалки** · basic · 1500–2000 · команды CLI, модули, vault, galaxy, lint, molecule, VMware, диагностика · → 03, 05, 11, 24, 60.
- `66-sources.md` — **Источники** · basic · 800–1200 · официальная документация, стандарты, инструменты, сообщества · → все разделы.

**Итого:** 59 страниц (включая главную и глоссарий), ~95–130 тыс. слов.

## 6. Карта ключевых перекрёстных ссылок

| Хаб | Связи |
|---|---|
| Inventory и филиалы | 05 ↔ 20, 24, 26, 30 |
| Секреты | 11 ↔ 12, 14, 15, 16, 53 |
| Безопасный код | 13 ↔ 07, 09, 50, 52, 62 |
| VMware | 24 ↔ 29, 30, 40, 44, 45 |
| Харденинг | 35 ↔ 21, 36–41, 44, 61 |
| Комплаенс | 44 ↔ 22, 35–43, 61 |
| Инциденты и EDA | 45 ↔ 37, 42, 46, 47 |
| Платформа | 53 ↔ 14, 15, 20, 30, 51, 54 |
| Эксплуатация | 60 ↔ все технические страницы |

## 7. Порядок генерации

| Партия | Страницы | Статус |
|---|---|---|
| 0 | OUTLINE.md, STYLEGUIDE.md, docs/index.md, docs/start/glossary.md, STATE.md | done |
| 1 | start/reading-paths, start/quickstart, fundamentals/01–03 | next |
| 2 | fundamentals/04–06 | planned |
| 3 | fundamentals/07–09, secure-dev/10 | planned |
| 4 | secure-dev/11–13 | planned |
| 5 | secure-dev/14–16, admin/20 | planned |
| 6 | admin/21–24 | planned |
| 7 | admin/25–28 | planned |
| 8 | admin/29–31, security/35 | planned |
| 9 | security/36–39 | planned |
| 10 | security/40–43 | planned |
| 11 | security/44–46 | planned |
| 12 | security/47–48, quality/50 | planned |
| 13 | quality/51–55 | planned |
| 14 | ops/60–63 | planned |
| 15 | ops/64–66, mkdocs.yml, README.md, CHANGELOG.md, финальная консистентность | planned |

Правила партии: 3–5 страниц; после каждой — самоотчёт, обновление `STATE.md`, список TODO и проверенных ссылок. При обрыве контекста продолжать с последнего незавершённого заголовка.

## 8. Открытые вопросы

1. Число филиалов и распределение хостов по площадкам.
2. vCenter: единый, региональные, или standalone ESXi; версии ESXi/vCenter.
3. Юрисдикция и перечень национальных/отраслевых требований.
4. SIEM/EDR: используемые продукты.
5. Вендоры сетевого оборудования.
6. CI-платформа: GitLab CE, GitHub Actions или другая.
7. Дистрибутив Kubernetes.
8. Наличие публичных облаков.
9. Минорные версии ОС.
10. Подтверждение формата MkDocs Material.

Ответы на вопросы 1–4 нужны до партий 5–11; остальные — до финальной консистентности.

## 9. Критерии готовности

- Все 59 страниц созданы по шаблону и frontmatter.
- Каждая страница содержит проверяемые примеры, проверку результата, blast radius и чек-лист.
- Нет выдуманных модулей, параметров и URL; версии указаны.
- Все относительные ссылки работают, nav в `mkdocs.yml` полон.
- Средняя оценка по рубрике приёмки ≥ 1,8, ни одного нуля.
- `README.md`, `CHANGELOG.md`, `STATE.md` актуальны.
