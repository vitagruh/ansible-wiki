---
title: "Источники"
slug: "sources"
part: "ops"
audience: ["sysadmin", "secops", "soc", "architect", "manager"]
level: "basic"
applies_to:
  ansible_core: ">=2.17"
  os: ["rhel9", "ubuntu24.04", "debian12"]
collections: ["ansible.builtin", "ansible.posix", "community.general", "community.vmware", "ansible.netcommon"]
security_impact: "low"
last_reviewed: "2026-11-11"
owners: ["tbd"]
---

# Источники

Список проверенных первоисточников, на которые опирается вики: официальная документация, стандарты, инструменты и сообщества. Каждая ссылка сопровождается назначением, чтобы отличать нормативный документ от практического руководства и блога.

## Зачем это нужно

Автоматизация быстро устаревает: модули переезжают между коллекциями, параметры объявляются deprecated, версии Python выходят из поддержки. Единственный способ не тиражировать устаревшие практики — сверяться с первоисточником и фиксировать версию, к которой относится утверждение.

Правила работы с источниками в этом проекте:

1. Нормативные требования подтверждаются документом стандарта, а не пересказом.
2. Поведение модуля подтверждается страницей документации той версии коллекции, которая закреплена в `requirements.yml`.
3. Ссылка без даты и версии считается ориентиром, а не доказательством.
4. Примеры из блогов и ответов на форумах проверяются на стенде до попадания в продакшн.

Для практической работы список делится на три уровня доверия. Нормативный уровень — стандарты и требования регуляторов: на них ссылаются в обоснованиях исключений. Технический уровень — документация вендора и коллекций: по ней проверяются параметры и поведение. Вспомогательный уровень — статьи, форумы и примеры: они помогают найти направление, но не служат доказательством.

## Как оценивать источник

| Критерий | Надёжный источник | Слабый источник |
|---|---|---|
| Автор | вендор, проект, орган стандартизации | анонимный пост |
| Версия | указана версия продукта или коллекции | «последняя версия» без деталей |
| Дата | есть дата публикации и обновления | без даты |
| Полнота | параметры, ограничения, примеры | только фрагмент кода |
| Проверяемость | ссылки на changelog и issue | утверждения без ссылок |

## Официальная документация Ansible

Документация Ansible — основной рабочий источник. У неё есть версионные разделы: адрес `latest` показывает текущую стабильную ветку, а для закреплённой версии используйте страницу релиза. При проверке параметра всегда смотрите, к какой версии коллекции относится страница: модуль мог переехать из `community.general` в отдельную коллекцию или потерять параметр.

| Ресурс | Для чего используется |
|---|---|
| [Ansible documentation](https://docs.ansible.com/ansible/latest/index.html) | точка входа во всю документацию |
| [Installation guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) | установка ansible-core, venv, pipx |
| [Release and maintenance](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html) | матрица версий и поддержка Python |
| [Configuration settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html) | параметры `ansible.cfg` и переменные окружения |
| [Interpreter discovery](https://docs.ansible.com/ansible/latest/reference_appendices/interpreter_discovery.html) | выбор Python на управляемых узлах |
| [Troubleshooting](https://docs.ansible.com/ansible/latest/reference_appendices/troubleshooting.html) | типовые ошибки соединения и выполнения |
| [FAQ](https://docs.ansible.com/ansible/latest/reference_appendices/faq.html) | частые вопросы по поведению ядра |
| [Playbook guide](https://docs.ansible.com/ansible/latest/playbook_guide/index.html) | playbooks, handlers, blocks, роли |
| [Best practices](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_best_practices.html) | структура проекта и соглашения |
| [Strategies](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_strategies.html) | `linear`, `free`, `serial`, `throttle` |
| [Error handling](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html) | `failed_when`, `ignore_errors`, rescue |
| [Delegation and rolling updates](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html) | `serial`, делегирование, `run_once` |
| [Vault](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vault.html) | шифрование секретов и vault ID |
| [Debugger](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_debugger.html) | пошаговая отладка задач |
| [Command line tools](https://docs.ansible.com/ansible/latest/command_guide/index.html) | `ansible`, `ansible-playbook`, `ansible-inventory` |
| [ansible-pull](https://docs.ansible.com/ansible/latest/cli/ansible-pull.html) | pull-модель для филиалов |
| [Collections guide](https://docs.ansible.com/ansible/latest/collections_guide/index.html) | установка и версионирование коллекций |
| [Index of all modules](https://docs.ansible.com/ansible/latest/collections/all_plugins.html) | проверка FQCN и параметров |

Документация коллекций — основной источник для конкретных модулей: [ansible.posix](https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html), [ansible.netcommon](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html), [community.vmware](https://docs.ansible.com/ansible/latest/collections/community/vmware/index.html), [kubernetes.core](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/index.html).

## Платформа и запуск

| Ресурс | Для чего используется |
|---|---|
| [AWX project](https://github.com/ansible/awx) | исходный код, релизы, известные ограничения |
| [Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible) | возможности подписочной платформы |
| [Automation Controller guide](https://docs.ansible.com/automation-controller/latest/html/userguide/index.html) | RBAC, credentials, workflows, аудит |
| [ansible-rulebook](https://github.com/ansible/ansible-rulebook) | Event-Driven Ansible, источники событий |

Для выбора между AWX, AAP и Semaphore используйте сравнение в [AAP, AWX, Semaphore](../quality/53-aap-awx.md), а не маркетинговые материалы.

## Стандарты и регуляторика

| Документ | Для чего используется |
|---|---|
| [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) | технические baseline для Linux и ESXi |
| [CIS Controls](https://www.cisecurity.org/controls) | управленческие контроли и приоритизация |
| [DISA STIGs](https://public.cyber.mil/stigs/) | профили STIG для RHEL и Ubuntu |
| [ISO/IEC 27001](https://www.iso.org/standard/27001) | требования к системе менеджмента ИБ |
| [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) | функции Identify, Protect, Detect, Respond, Recover |
| [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/final) | каталог контролей и их формулировки |
| [MITRE ATT&CK](https://attack.mitre.org/) | моделирование техник атак и детектов |
| [NVD](https://nvd.nist.gov/) | идентификаторы CVE и оценки CVSS |
| [FIRST CVSS](https://www.first.org/cvss/) | методика оценки уязвимостей |
| [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280) | профиль X.509 для PKI |

Стандарты не копируются в playbook дословно: они переводятся в проверяемые контроли и доказательства, как описано в [Комплаенсе](../security/44-compliance.md). Для CIS и STIG одновременно выбирается основной профиль, а пересечения сопоставляются.

Отдельно учитывайте версию стандарта: CIS Benchmarks обновляются под минорные версии ОС, а STIG выходят отдельными релизами. Ссылка на benchmark без указания версии не позволяет воспроизвести проверку, поэтому в реестре доказательств фиксируются профиль, версия и дата применения.

## Инструменты

Инструменты из списка закрывают три задачи: проверку кода до запуска, тестирование роли в изоляции и доказательство соответствия baseline. Не пытайтесь внедрить все сразу: начните с линтера в CI, затем добавьте Molecule для переиспользуемых ролей и только потом сканер соответствия.

| Инструмент | Для чего используется |
|---|---|
| [ansible-lint](https://ansible.readthedocs.io/projects/lint/) | статический анализ playbook и ролей |
| [ansible-lint repository](https://github.com/ansible/ansible-lint) | правила, changelog, обсуждение ложных срабатываний |
| [Molecule](https://ansible.readthedocs.io/projects/molecule/) | сценарии тестирования ролей и идемпотентность |
| [Molecule repository](https://github.com/ansible-community/molecule) | драйверы, примеры, миграция версий |
| [dev-sec linux-baseline](https://github.com/dev-sec/linux-baseline) | базовый харденинг Linux в виде роли |
| [dev-sec ssh-baseline](https://github.com/dev-sec/ssh-baseline) | проверки конфигурации SSH |
| [ansible-lockdown](https://github.com/ansible-lockdown) | роли CIS и STIG для RHEL, Ubuntu, Debian |
| [ComplianceAsCode content](https://github.com/ComplianceAsCode/content) | SCAP-профили и правила |
| [OpenSCAP](https://www.open-scap.org/) | сканирование и отчёты о соответствии |
| [Ansible Galaxy](https://galaxy.ansible.com/) | публичные коллекции и роли |
| [x509_certificate module](https://docs.ansible.com/ansible/latest/collections/community/crypto/x509_certificate_module.html) | выпуск сертификатов в PKI-сценариях |

Правило снабжения: инструмент попадает в пайплайн только с закреплённой версией и проверенным источником. Цепочка поставок описана в [Безопасности цепочки поставок](../secure-dev/15-supply-chain.md).

## VMware

| Ресурс | Для чего используется |
|---|---|
| [vSphere 8 documentation](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0.html) | администрирование vCenter и ESXi |
| [community.vmware collection](https://docs.ansible.com/ansible/latest/collections/community/vmware/index.html) | модули для ВМ, снапшотов, хостов |
| [community.vmware repository](https://github.com/ansible-collections/community.vmware) | исходный код, issues, ограничения версий |

Перед изменением всегда сверяйтесь с разделом Return Values и Notes конкретного модуля: часть операций требует vCenter, а не standalone ESXi. Практики — в [VMware ESXi и vCenter](../admin/24-vmware-esxi.md).

## Linux, Python и SELinux

| Ресурс | Для чего используется |
|---|---|
| [RHEL 9 documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9) | SELinux, пакеты, systemd |
| [Ubuntu Server documentation](https://ubuntu.com/server/docs) | пакеты, netplan, AppArmor |
| [Debian documentation](https://www.debian.org/doc/) | политики и руководства администратора |
| [SELinux Notebook](https://github.com/SELinuxProject/selinux-notebook) | устройство политики и типовые отказы |
| [Python 3 documentation](https://docs.python.org/3/) | версии, venv, совместимость |
| [pipx](https://pipx.pypa.io/stable/) | изолированная установка CLI |

Различия дистрибутивов влияют на имена пакетов, сервисов и путей, поэтому проверка выполняется на той ОС, которая есть в филиале. Матрица версий — в [Установке и версионировании](../fundamentals/03-install.md).

## Сообщества

| Ресурс | Для чего используется |
|---|---|
| [Ansible forum](https://forum.ansible.com/) | обсуждение поведения модулей и ошибок |
| [Community communication](https://docs.ansible.com/ansible/latest/community/communication.html) | каналы проекта и правила общения |
| [Ansible on GitHub](https://github.com/ansible/ansible) | issues, changelog, исходный код ядра |
| [Stack Overflow: ansible](https://stackoverflow.com/questions/tagged/ansible) | типовые ошибки и примеры |

Ответы сообщества полезны для поиска направления, но не являются нормативным источником. Перед применением проверяйте версию, контекст и безопасность примера.

Отдельно стоит упомянуть русскоязычные материалы: они удобны для быстрого введения в тему, но почти всегда отстают от версий и не содержат ссылок на changelog. Используйте их как объяснение концепции, а параметры и имена модулей сверяйте с официальной документацией.

## Внутренние источники

Не всё, что нужно для работы, публикуется вендорами. Часть знаний существует только внутри организации, и эти источники должны быть такими же проверяемыми, как внешние.

| Источник | Что содержит | Кто ведёт |
|---|---|---|
| CMDB | хосты, владельцы, площадки, критичность | служба эксплуатации |
| Паспорт объекта | схема сети, адресация, точки входа | сетевой архитектор |
| Реестр исключений | отклонения от baseline и сроки | SecOps |
| Runbook | порядок восстановления и отката | владелец сервиса |
| Журнал изменений | кто, что и когда менял | change management |
| Реестр секретов | владельцы, срок ротации, способ хранения | ИБ |

Playbook, который ссылается на CMDB и runbook, легче поддерживать: при смене площадки обновляется один источник, а не комментарии в роли. Внутренние документы стоит версионировать в том же ритме, что и код автоматизации.

## Поддержание списка

Список пересматривается раз в квартал и при каждом изменении baseline: новая версия ansible-core, переход на другую коллекцию, обновление стандарта. Владелец страницы проверяет, что ссылки открываются, версии в тексте совпадают с `requirements.yml`, а устаревшие инструменты заменены.

Если ссылка перестала открываться, не заменяйте её первой найденной в поиске: найдите раздел на официальном сайте вручную и проверьте, что он относится к поддерживаемой версии. Практика показывает, что половина «новых» материалов в поиске — копии документации двух-трёхлетней давности.

Признаки устаревшей ссылки: редирект на общую страницу, отсутствие версии в заголовке, упоминание ansible 2.9, примеры с `with_*` вместо `loop`, модули без FQCN. Такие ссылки заменяются, а не оставляются «на всякий случай»: устаревший источник хуже отсутствующего, потому что создаёт ложную уверенность.

## Чего избегать

| Источник | Почему |
|---|---|
| Устаревшие статьи под ansible 2.9 | другой синтаксис, модули без FQCN |
| Копии документации без версии | неизвестно, к какой версии относится текст |
| Примеры с `validate_certs: false` | ослабляют защиту и тиражируются |
| Роли без владельца и версии | риск цепочки поставок |
| Ответы от генеративных моделей без проверки | возможны несуществующие параметры |

## Проверка актуальности

```bash
ansible --version
ansible-config dump --only-changed
ansible-galaxy collection list
ansible-doc community.vmware.vmware_guest
```

`ansible --version` показывает версию ядра и путь к конфигурации, `collection list` — фактические версии коллекций. Если версия в документации не совпадает с установленной, ориентируйтесь на установленную и планируйте обновление отдельным изменением.

Полезно хранить снимок версий рядом с релизом: файл `pip freeze` и вывод `ansible-galaxy collection list`. Через полгода именно он объяснит, почему поведение отличалось от текущей документации. Без такого снимка разбор старого инцидента превращается в реконструкцию по памяти.

## Безопасность

Работа с источниками — часть цепочки поставок. Скачивание ролей и коллекций с непроверенных зеркал, запуск примеров из чатов и копирование команд с `curl | bash` создают риск выполнения чужого кода на control node. Допустимы только официальные репозитории, внутреннее зеркало и проверенные артефакты с контрольными суммами.

## Чек-лист

- [ ] Для каждого технического утверждения найден первоисточник с версией.
- [ ] Версия документа совпадает с версией в `requirements.yml`.
- [ ] Нормативные требования взяты из документа стандарта.
- [ ] Примеры из сообщества проверены на стенде.
- [ ] Ссылки на инструменты ведут в официальные репозитории.
- [ ] Источники пересматриваются при обновлении baseline.

## Источники

- [Ansible documentation](https://docs.ansible.com/ansible/latest/index.html)
- [Ansible releases and changelogs](https://github.com/ansible/ansible/releases)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [VMware vSphere documentation](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/8-0.html)

## Связанные страницы

- [Установка и версионирование](../fundamentals/03-install.md)
- [Диагностика и troubleshooting](60-troubleshooting.md)
- [Чек-листы](61-checklists.md)
- [FAQ](64-faq.md)
- [Комплаенс и доказательства](../security/44-compliance.md)
- [Безопасность цепочки поставок](../secure-dev/15-supply-chain.md)
- [Харденинг Linux](../security/35-linux-hardening.md)
- [Глоссарий](../start/glossary.md)
