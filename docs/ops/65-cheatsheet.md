---
title: "Шпаргалки"
slug: "cheatsheet"
part: "ops"
audience: ["sysadmin", "secops", "soc", "architect"]
level: "basic"
applies_to:
  ansible_core: ">=2.17"
  os: ["rhel9", "ubuntu24.04", "debian12"]
collections: ["ansible.builtin", "ansible.posix", "community.general", "community.vmware", "ansible.netcommon"]
security_impact: "low"
last_reviewed: "2026-11-11"
owners: ["tbd"]
---

# Шпаргалки

Компактный справочник команд и соответствий «задача → модуль» для повседневной работы. Все примеры рассчитаны на ansible-core 2.17+ и предполагают, что inventory и `ansible.cfg` уже настроены.

## Зачем это нужно

Во время инцидента нет времени искать синтаксис `--limit` или имя модуля для SELinux. Шпаргалка снижает число ошибок в спешке и напоминает безопасные значения по умолчанию: `host_key_checking = True`, `validate_certs: true`, секреты только через vault. Команды, меняющие систему, отмечены — их не стоит запускать без `--check` и окна обслуживания.

## Как читать шпаргалку

Разделы соответствуют типовому рабочему дню: проверка соединения, запуск, секреты, зависимости, тесты, VMware и сеть. Команды приведены в виде, готовом к копированию, но пути и имена inventory нужно заменить на свои. Блоки, которые меняют систему, сопровождаются пояснением о риске; остальные предназначены для чтения состояния.

Шпаргалка не заменяет документацию модуля. Перед использованием незнакомого параметра откройте `ansible-doc` с полным FQCN: это исключает ситуацию, когда параметр принадлежит другому модулю или удалён в текущей версии коллекции.

## Базовые команды CLI

```bash
ansible --version
ansible-config dump --only-changed
ansible-config init --disabled -t all > ansible.cfg.sample
ansible-doc ansible.builtin.copy
ansible-doc -l | grep -i selinux
ansible-inventory --graph
ansible-inventory --host msk-app01
ansible-inventory --list --yaml
```

Запуск и проверка playbook:

```bash
ansible-playbook -i inventories/prod/hosts.yml site.yml --syntax-check
ansible-playbook -i inventories/prod/hosts.yml site.yml --check --diff
ansible-playbook -i inventories/prod/hosts.yml site.yml --list-tasks --list-hosts
ansible-playbook -i inventories/prod/hosts.yml site.yml --limit branch_msk --tags ntp
ansible-playbook -i inventories/prod/hosts.yml site.yml --start-at-task "Deploy sshd fragment"
ansible-playbook -i inventories/prod/hosts.yml site.yml --step
ansible-playbook -i inventories/prod/hosts.yml site.yml -e @vars/prod.yml --ask-become-pass
```

`--check` не гарантирует отсутствие изменений: задачи с `command` и `shell` в check mode могут не выполняться или вести себя иначе. Для рискованных изменений сначала `--check --diff`, затем `--limit` на один хост, затем партии.

`--list-tasks` и `--list-hosts` выполняются без подключения к хостам и безопасны в любой момент. `--start-at-task` полезен при разборе длинного playbook, но пропускает обработчики и зависимости, поэтому не используйте его для продакшн-раскатки. `--step` требует подтверждения каждой задачи и удобен только на стенде или при отладке одного хоста.

## Ad-hoc команды

Ad-hoc запуск применяется для чтения состояния, а не для изменений. Типовые безопасные примеры:

```bash
ansible branches -m ansible.builtin.ping
ansible branches -m ansible.builtin.setup -a "filter=ansible_distribution*"
ansible msk-app01 -m ansible.builtin.command -a "systemctl is-active sshd" -b
ansible branches -m ansible.builtin.service_facts
ansible switches -m ansible.netcommon.cli_command -a "command='show version'"
```

Флаг `-b` добавляйте только там, где без него команда не выполнится. Для чтения `systemctl is-active` привилегии не нужны. Если ad-hoc команда меняет систему, это признак того, что изменение должно быть оформлено ролью: иначе оно не попадёт в Git и не будет проверено.

## Конфигурация и окружение

```ini
[defaults]
inventory = inventories/prod/hosts.yml
collections_path = ./collections
host_key_checking = True
timeout = 20
forks = 25
stdout_callback = ansible.posix.debug
callbacks_enabled = ansible.posix.profile_tasks, ansible.posix.timer
log_path = ./logs/ansible.log
interpreter_python = auto_silent

[ssh_connection]
pipelining = True
```

Переменные окружения для разовых проверок:

```bash
ANSIBLE_CONFIG=./ansible.cfg ansible-playbook site.yml
ANSIBLE_STDOUT_CALLBACK=ansible.posix.debug ansible-playbook site.yml
ANSIBLE_ENABLE_TASK_DEBUGGER=true ansible-playbook site.yml --limit msk-app01
ANSIBLE_LOG_PATH=./logs/run.log ansible-playbook site.yml
```

`pipelining = True` требует отключённого `requiretty` в sudoers и работает не со всеми модулями. Включайте после проверки на лабораторном хосте. Детали — в [Конфигурации ansible.cfg](../fundamentals/04-config.md).

Порядок приоритета конфигурации: переменные окружения, `ansible.cfg` в текущем каталоге, файл из домашнего каталога, затем `/etc/ansible/ansible.cfg`. Если поведение не совпадает с ожидаемым, выполните `ansible-config dump --only-changed` и посмотрите, из какого файла взято значение. Частая ошибка — запуск из каталога, где лежит другой `ansible.cfg`.

## Inventory и паттерны

```bash
ansible all -i inventories/prod/hosts.yml -m ansible.builtin.ping
ansible branches -i inventories/prod/hosts.yml -m ansible.builtin.setup
ansible 'branch_*' -i inventories/prod/hosts.yml -m ansible.builtin.ping
ansible 'branches:!branch_spb' -i inventories/prod/hosts.yml -m ansible.builtin.ping
ansible 'branch_msk:&app' -i inventories/prod/hosts.yml -m ansible.builtin.ping
ansible '~^msk-' -i inventories/prod/hosts.yml -m ansible.builtin.ping
ansible-playbook site.yml --limit @retry_hosts.txt
```

| Паттерн | Значение |
|---|---|
| `all` | все хосты inventory |
| `branch_msk` | группа филиала |
| `branch_*` | все группы с префиксом |
| `branches:!branch_spb` | объединение с исключением |
| `branch_msk:&app` | пересечение групп |
| `~^msk-` | регулярное выражение по именам |
| `@file` | список хостов из файла |

Паттерны проверяйте через `--list-hosts`: ошибка в одном символе отправляет playbook не в тот филиал. Синтаксис и иерархия — в [Inventory и группы](../fundamentals/05-inventory.md).

## Vault

```bash
ansible-vault create group_vars/all/vault.yml
ansible-vault edit group_vars/all/vault.yml
ansible-vault view group_vars/all/vault.yml
ansible-vault encrypt secrets/plain.yml
ansible-vault decrypt secrets/plain.yml
ansible-vault rekey --new-vault-id prod@prompt group_vars/all/vault.yml
ansible-vault encrypt_string --name 'db_password' 'change-me'
```

Запуск с несколькими vault ID:

```bash
ansible-playbook site.yml --vault-id dev@~/.vault/dev --vault-id prod@prompt
```

Правила: пароль vault вне репозитория, права `0600`, отдельный vault ID на среду, `no_log: true` на задачах с секретами. `encrypt_string` удобен для одной переменной, но не заменяет структурированный vault-файл. Полный подход — в [Управлении секретами](../secure-dev/11-secrets.md).

Если playbook завершается ошибкой расшифровки, проверьте, что используется тот же vault ID, что и при шифровании. Список ID виден по префиксу в заголовке файла; при смене пароля используйте `rekey`, а не повторное шифрование поверх старого файла.

## Galaxy и коллекции

```bash
ansible-galaxy collection install -r requirements.yml -p ./collections
ansible-galaxy collection list
ansible-galaxy collection verify community.general
ansible-galaxy collection install ansible.posix:1.5.4
ansible-galaxy role install -r requirements.yml -p ./roles
ansible-galaxy role init my_namespace.myrole
ansible-galaxy collection init my_namespace.my_collection
ansible-galaxy collection build
```

`ansible-galaxy collection verify` сверяет установленную коллекцию с источником, если она не менялась локально. Для Git-ролей фиксируйте полный хэш коммита. Снабжение и подписи — в [Безопасности цепочки поставок](../secure-dev/15-supply-chain.md).

Каталог `./collections` добавляйте в `.gitignore`: в репозитории хранится `requirements.yml`, а не скачанный контент. Версии в `requirements.yml` и в CI должны совпадать, иначе тесты проверяют не тот код, который попадёт на control node.

## Линт и проверки

```bash
yamllint -c .yamllint .
ansible-lint site.yml
ansible-lint --profile production site.yml
ansible-lint -x no-changed-when site.yml
ansible-lint --fix site.yml
```

Профиль `production` строже остальных и включает проверки FQCN, имен задач и безопасности. Пропуск правила через `-x` допустим только с комментарием в PR. Набор тестов — в [Тестировании автоматизации](../quality/50-testing.md).

`yamllint` и `ansible-lint` проверяют разные вещи: первый — форматирование и синтаксис YAML, второй — практики Ansible. Запускайте оба в CI, иначе часть замечаний появится только на ревью. Локально удобно вызывать `ansible-lint` из того же venv, что и ansible-core, иначе версии правил разойдутся с CI.

## Molecule

```bash
molecule init role my_namespace.myrole --driver-name docker
molecule create
molecule converge
molecule idempotence
molecule verify
molecule test
molecule login
molecule destroy
molecule list
```

`molecule test` выполняет полный цикл, включая проверку идемпотентности. Для матрицы ОС используйте несколько сценариев или платформ в `molecule.yml`. Контейнеры не подходят для тестов, требующих systemd, — там нужны ВМ.

Драйвер Docker быстрее, но не воспроизводит SELinux и ядро боевого хоста. Если роль меняет sshd, firewall или загрузчик, тестируйте на ВМ с той же версией ОС, что в филиале. Результат `molecule test` без шага `idempotence` не доказывает идемпотентность.

## VMware

```bash
ansible-galaxy collection install community.vmware
ansible-doc -l community.vmware | grep -i guest
ansible-doc community.vmware.vmware_guest
openssl s_client -connect vcenter.example.internal:443 -servername vcenter.example.internal </dev/null
```

Проверка API и прав без изменения инфраструктуры:

```yaml
---
- name: Read VMware inventory facts
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Get VM info
      community.vmware.vmware_guest_info:
        hostname: "{{ vcenter_hostname }}"
        username: "{{ vcenter_username }}"
        password: "{{ vcenter_password }}"
        validate_certs: true
        port: 443
        name: msk-app01
      register: vm

    - name: Show power state
      ansible.builtin.debug:
        msg: "{{ vm.instance.power_state }}"
```

Учётные данные — из vault, проверка сертификата включена. Операции с ВМ и снапшотами — в [VMware ESXi и vCenter](../admin/24-vmware-esxi.md).

`module_defaults` избавляет от повторения параметров подключения в каждой задаче. Не увеличивайте `forks` для задач VMware: vCenter ограничивает число одновременных сессий, и при перерасходе появляется ошибка о слишком большом числе клиентов.

## Сетевые устройства

```bash
ansible-doc ansible.netcommon.cli_command
ansible-doc ansible.netcommon.cli_config
ansible-playbook -i inventories/network/hosts.yml backup.yml --limit sw_msk
```

```yaml
- name: Backup device configuration
  hosts: switches
  gather_facts: false
  connection: ansible.netcommon.network_cli

  tasks:
    - name: Read running config
      ansible.netcommon.cli_command:
        command: show running-config
      register: cfg
      changed_when: false

    - name: Store configuration
      ansible.builtin.copy:
        content: "{{ cfg.stdout }}\n"
        dest: "backups/{{ inventory_hostname }}.cfg"
        mode: "0640"
      delegate_to: localhost
```

Для `network_cli` обязательны `ansible_network_os` и коллекция вендора. Таймаут команд задаётся `ansible_command_timeout`.

Бэкап конфигурации выполняется до изменений и сохраняется как артефакт с датой. Сравнение с baseline удобно делать через `diff` между текущим и предыдущим файлом: это дешевле, чем разбирать последствия массового изменения на устройстве.

## Диагностика

```bash
ansible all -m ansible.builtin.ping -vvv
ansible msk-app01 -m ansible.builtin.setup -a "filter=ansible_python_version"
ansible msk-app01 -m ansible.builtin.raw -a "python3 --version"
ssh -vv -o ConnectTimeout=10 svc-ansible@192.0.2.31
ansible-config dump --only-changed
ansible-playbook site.yml --check --diff --limit msk-app01
```

```yaml
- name: Pause on failure for inspection
  hosts: msk-app01
  gather_facts: true
  debugger: on_failed
```

В отладчике: `p result`, `p task.args`, `p task_vars['inventory_hostname']`, `redo`, `continue`, `quit`. Деревья решений — в [Диагностике и troubleshooting](60-troubleshooting.md).

Перед публикацией вывода `-vvv` в тикете удалите пути, имена пользователей и значения переменных. Если нужен полный лог для разбора, включите `log_path` на короткое время и ограничьте доступ к файлу: он содержит те же данные, что и консоль.

## Таблица модулей

| Задача | Модуль | Примечание |
|---|---|---|
| Установить пакет | `ansible.builtin.package` | выбирает dnf или apt по фактам |
| Обновить только пакет | `ansible.builtin.dnf` / `ansible.builtin.apt` | не использовать `state: latest` без нужды |
| Управлять сервисом | `ansible.builtin.systemd_service` | для systemd-юнитов |
| Разложить файл | `ansible.builtin.copy` | `mode` и владелец обязательны |
| Разложить шаблон | `ansible.builtin.template` | с `validate` для конфигов |
| Создать каталог | `ansible.builtin.file` | `state: directory` |
| Изменить строку | `ansible.builtin.lineinfile` | осторожно с регулярными выражениями |
| Создать пользователя | `ansible.builtin.user` | `password` только из vault |
| Добавить SSH-ключ | `ansible.posix.authorized_key` | `exclusive` требует полноты списка |
| Настроить cron | `ansible.builtin.cron` | `name` обязателен |
| Настроить sysctl | `ansible.posix.sysctl` | `sysctl_file` и `reload` |
| Настроить firewalld | `ansible.posix.firewalld` | проверяйте зоны |
| Настроить ufw | `community.general.ufw` | не отключайте firewall целиком |
| Режим SELinux | `ansible.posix.selinux` | `state: enforcing` |
| Контекст SELinux | `community.general.sefcontext` | затем `restorecon` |
| Boolean SELinux | `ansible.posix.seboolean` | минимально необходимый |
| Смонтировать ФС | `ansible.posix.mount` | проверяйте `fstab` |
| Скачать файл | `ansible.builtin.get_url` | с `checksum` |
| Вызвать API | `ansible.builtin.uri` | `validate_certs: true` |
| Перезагрузить хост | `ansible.builtin.reboot` | с `serial: 1` |
| Дождаться порта | `ansible.builtin.wait_for` | `timeout` и `delay` |
| Клонировать ВМ | `community.vmware.vmware_guest` | `wait` и `template` |
| Снапшот ВМ | `community.vmware.vmware_guest_snapshot` | не заменяет бэкап |
| Команда на устройстве | `ansible.netcommon.cli_command` | только чтение — `changed_when: false` |
| Применить конфиг | `ansible.netcommon.cli_config` | с бэкапом и `serial: 1` |
| Объект Kubernetes | `kubernetes.core.k8s` | с `state: present` |

Модуль выбирается по смыслу, а не по привычке: `command` и `shell` — крайний случай, когда готового модуля нет. Правила — в [Модулях и FQCN](../fundamentals/09-modules.md).

## Версии и совместимость

| Компонент | Проверка | Базовое значение |
|---|---|---|
| ansible-core | `ansible --version` | 2.17+ |
| Python на control node | `python3 --version` | 3.10–3.12 |
| Python на управляемом узле | `ansible host -m setup -a "filter=ansible_python_version"` | 3.7–3.12, на RHEL 8 — `python39` |
| Коллекции | `ansible-galaxy collection list` | версии из `requirements.yml` |
| ОС | `ansible host -m setup -a "filter=ansible_distribution*"` | RHEL/Rocky/Alma 8–9, Ubuntu 22.04/24.04, Debian 12 |

Проверяйте версии до запуска, а не после ошибки. Если управляемый узел отвечает версией Python вне диапазона, задача завершится с неинформативным сообщением модуля; тогда поможет `ansible.builtin.raw` и явный `ansible_python_interpreter`.

## Проверка перед запуском

Перед запуском полезно потратить минуту на проверку цели, а не на чтение всего playbook. Три команды ниже показывают, куда пойдёт изменение и что оно сделает.

- [ ] Выбран правильный inventory и паттерн проверен через `--list-hosts`.
- [ ] `--syntax-check` и `--check --diff` пройдены.
- [ ] Понятно, какие задачи не поддерживают check mode.
- [ ] Секреты не передаются через `-e` и не попадают в вывод.
- [ ] Для рискованных изменений заданы `serial` и план отката.
- [ ] Открыта вторая сессия или есть out-of-band доступ.

## Безопасность

| Команда | Риск | Безопасная альтернатива |
|---|---|---|
| `-vvv` на проде | секреты в логах | `no_log`, очистка вывода |
| `--limit all` по ошибке | массовое изменение | явная группа, `serial` |
| `ansible-doc` без FQCN | не тот модуль из другой коллекции | полное имя |
| `validate_certs: false` | перехват API | установить CA |
| `state: latest` на всём парке | незапланированные обновления | пиннинг версий |

Административные команды меняют состояние сразу и без проверки. Если команда необходима для диагностики, ограничьте её одним хостом через `--limit` и убедитесь, что она не пишет на диск. Для повторяемых действий используйте playbook: он оставляет след в Git и может быть проверен до запуска.

## Источники

- [Ansible command line tools](https://docs.ansible.com/ansible/latest/command_guide/index.html)
- [Index of all modules and plugins](https://docs.ansible.com/ansible/latest/collections/all_plugins.html)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vault.html)
- [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html)
- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [Molecule](https://ansible.readthedocs.io/projects/molecule/)
- [community.vmware collection](https://docs.ansible.com/ansible/latest/collections/community/vmware/index.html)
- [ansible.netcommon collection](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html)

## Связанные страницы

- [Установка и версионирование](../fundamentals/03-install.md)
- [Inventory и группы](../fundamentals/05-inventory.md)
- [Управление секретами](../secure-dev/11-secrets.md)
- [VMware ESXi и vCenter](../admin/24-vmware-esxi.md)
- [Диагностика и troubleshooting](60-troubleshooting.md)
- [Анти-паттерны](62-antipatterns.md)
- [FAQ](64-faq.md)
