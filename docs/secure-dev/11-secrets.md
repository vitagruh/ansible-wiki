---
title: "Управление секретами"
slug: "secrets"
part: "secure-dev"
audience: ["sysadmin", "secops", "architect"]
level: "advanced"
applies_to:
  ansible_core: ">=2.17"
  os: ["rhel9", "ubuntu24.04", "debian12"]
collections: ["ansible.builtin", "community.hashi_vault", "community.sops"]
security_impact: "critical"
last_reviewed: "2026-11-11"
owners: ["tbd"]
---

# Управление секретами

Секрет в playbook — это компрометация в Git, логах и резервных копиях. Ansible предлагает несколько механизмов: `ansible-vault`, внешние хранилища, SOPS и credentials платформы. Выбор зависит от масштаба, требований аудита и возможности выхода в сеть.

## 1. Зачем это нужно

Автоматизация без секретов невозможна: пароли БД, API-токены vCenter, ключи PEM, bind-пароли. Если хранить их в открытом виде, любой, кто читает репозиторий, получает доступ к инфраструктуре. Если передавать через `-e`, секрет остаётся в истории shell и журнале процесса. Нужен управляемый жизненный цикл: создание, выдача, использование, ротация, отзыв.

## 2. Ключевые понятия

| Понятие | Назначение |
|---|---|
| `ansible-vault` | шифрование файлов и строк паролем |
| Vault ID | метка набора секретов и пароля |
| Vault password file | файл с паролем для неинтерактивного запуска |
| `!vault` | зашифрованное значение внутри YAML |
| Внешнее хранилище | HashiCorp Vault, SOPS, cloud KMS |
| AAP credentials | секреты, хранимые платформой и внедряемые при запуске |
| `no_log` | подавление вывода задачи с секретом |
| Ротация | плановая замена секрета и отзыв старого |

## 3. Схема жизненного цикла

```mermaid
flowchart LR
    C[Создание секрета] --> S[Хранилище: vault / Vault / KMS]
    S --> I[Внедрение при запуске]
    I --> U[Использование на хосте]
    U --> R[Ротация]
    R --> V[Отзыв старого]
    V --> S
```

Секрет не должен попадать в Git в открытом виде ни на одном этапе. Даже временный файл с секретом требует прав `0600` и удаления после использования.

## 4. ansible-vault: базовый сценарий

Создание зашифрованного файла:

```bash
ansible-vault create --vault-id prod@prompt group_vars/all/vault.yml
```

Содержимое до шифрования:

```yaml
vault_db_password: "CHANGE_ME"
vault_api_token: "CHANGE_ME"
```

Открытые переменные ссылаются на зашифрованные:

```yaml
# group_vars/all/vars.yml
db_password: "{{ vault_db_password }}"
api_token: "{{ vault_api_token }}"
```

Файл `group_vars/all/vault.yml` автоматически загружается вместе с inventory. Пароль vault хранится отдельно:

```bash
install -m 0600 /dev/null ~/.ansible/vault-prod.pass
ansible-vault encrypt_string --vault-id prod@prompt --stdin-name 'vault_db_password'
```

В `ansible.cfg`:

```ini
[defaults]
vault_password_file = ~/.ansible/vault-prod.pass
```

Для нескольких сред используйте разные Vault ID:

```bash
ansible-playbook site.yml --vault-id prod@~/.ansible/vault-prod.pass
```

Проверка и редактирование:

```bash
ansible-vault view --vault-id prod@prompt group_vars/all/vault.yml
ansible-vault edit --vault-id prod@prompt group_vars/all/vault.yml
ansible-vault rekey --vault-id prod@prompt --new-vault-id prod2@prompt group_vars/all/vault.yml
```

После `rekey` обновите файлы паролей и CI-переменные. Старый пароль должен быть отозван.

## 5. Использование в playbook

```yaml
---
- name: Deploy application environment
  hosts: branches
  become: true
  gather_facts: false

  tasks:
    - name: Render application environment file
      ansible.builtin.template:
        src: templates/app.env.j2
        dest: /etc/app/app.env
        owner: root
        group: root
        mode: "0600"
        validate: "grep -q '^DB_PASSWORD=' %s"
      no_log: true
      notify: Restart application

  handlers:
    - name: Restart application
      ansible.builtin.service:
        name: app
        state: restarted
```

`no_log: true` скрывает аргументы и результат задачи. Он не делает секрет невидимым для процесса на хосте и не заменяет права `0600`. Не передавайте секреты аргументами командной строки: они видны в `ps`.

## 6. Сравнение способов

| Способ | Где хранится | Аудит | Ротация | Air-gapped | Сложность |
|---|---|---|---|---|---|
| `ansible-vault` | Git | история Git, но без детального доступа | вручную | да | низкая |
| HashiCorp Vault | внешний сервис | подробный, с TTL и политиками | автоматическая | возможна | высокая |
| SOPS + KMS | Git + KMS | зависит от KMS | через KMS | ограниченно | средняя |
| Cloud KMS | облачный сервис | подробный | автоматическая | нет | средняя |
| AAP credentials | платформа | аудит запусков | вручную или API | да | средняя |

Для филиальной сети без постоянного канала `ansible-vault` остаётся рабочим минимумом. При наличии внутреннего Vault или AAP используйте их: они дают TTL, аудит и централизованный отзыв.

## 7. Внешние хранилища

Коллекции `community.hashi_vault` и `community.sops` позволяют получать секреты во время выполнения. Общий принцип: control node аутентифицируется короткоживущим токеном, получает только нужный секрет и не сохраняет его на диск.

Требования к интеграции:

- TLS с проверкой сертификата;
- аутентификация по сервисному аккаунту, а не по личному токену;
- политика least privilege на конкретный путь;
- TTL токена и автоматическое обновление;
- аудит чтения секрета;
- отказ от кэширования секрета в переменных дольше одной задачи.

AAP credentials предпочтительны, если платформа уже используется: секрет не попадает в playbook и не отображается в логах задания.

## 8. Ротация

Порядок ротации:

1. Создайте новый секрет в хранилище, не удаляя старый.
2. Обновите конфигурацию на canary-хосте с `no_log`.
3. Перезапустите сервис и проверьте здоровье.
4. Раскатайте на остальные хосты партиями.
5. Отзовите старый секрет.
6. Зафиксируйте изменение и доказательства.

Для баз данных и API используйте период, когда оба секрета действительны. Иначе ротация приведёт к отказу сервиса.

## 9. Безопасность и blast radius

| Риск | Последствие | Мера |
|---|---|---|
| Vault-пароль рядом с vault-файлом | расшифровка всех секретов | пароль вне Git, права `0600` |
| Секрет в `-e` | история shell и `ps` | `--vault-password-file`, не `-e` |
| `no_log` без проверки ошибок | сложная диагностика | отдельный diagnostic-режим без секретов |
| `debug: var=hostvars` | утечка всех переменных | точечный вывод |
| Ротация без перекрытия | простой сервиса | два активных секрета на время перехода |
| Секрет в backup-файле | утечка из копии | исключить каталог, шифровать backup |

## 10. Комплаенс-маппинг

| Требование | Как закрывается |
|---|---|
| CIS Control 3 | управление данными и секретами |
| NIST CSF 2.0 PR.AA | аутентификация и управление доступом |
| ISO/IEC 27001:2022 A.5.17 | аутентификационная информация |
| ISO/IEC 27001:2022 A.8.24 | криптография и управление ключами |

## 11. Типичные ошибки и troubleshooting

| Симптом | Причина | Проверка | Решение |
|---|---|---|---|
| `Vault password not found` | не передан vault ID | `ansible-playbook -vvv` | указать `--vault-id` или файл |
| `Decryption failed` | неверный пароль или повреждён файл | `ansible-vault view` | восстановить из Git, проверить пароль |
| Секрет виден в diff | `--diff` и отсутствие `no_log` | вывод `--check --diff` | добавить `no_log`, ограничить diff |
| Задача падает без деталей | `no_log` скрывает ошибку | временно отключить для диагностики | проверить в лаборатории, не в продакшене |
| Старый секрет действует | ротация не завершена | проверка в хранилище | отозвать старый, обновить конфиг |
| Vault-файл не загружается | неверный путь group_vars | `ansible-inventory --host` | положить файл рядом с inventory |

## 12. Чек-лист

- [ ] В Git нет открытых секретов.
- [ ] Vault-пароль хранится вне репозитория с правами `0600`.
- [ ] Для сред используются разные Vault ID.
- [ ] Задачи с секретами имеют `no_log: true`.
- [ ] Секреты не передаются через `-e` и аргументы команд.
- [ ] Ротация включает период перекрытия и отзыв старого секрета.
- [ ] Доступ к хранилищу аудируется и ограничен.
- [ ] Резервные копии не содержат открытых секретов.

## 13. Источники

- [Protecting sensitive data with Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [ansible-vault CLI](https://docs.ansible.com/ansible/latest/cli/ansible-vault.html)
- [community.hashi_vault](https://docs.ansible.com/ansible/latest/collections/community/hashi_vault/index.html)
- [community.sops](https://docs.ansible.com/ansible/latest/collections/community/sops/index.html)
- [Ansible Automation Platform credentials](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/)

## 14. Связанные страницы

- [Модель угроз автоматизации](10-threat-model.md)
- [Доступ и привилегии](12-access.md)
- [Секреты в CI/CD](14-cicd-secrets.md)
- [Безопасность цепочки поставок](15-supply-chain.md)
- [AAP, AWX, Semaphore](../quality/53-aap-awx.md)
- [Переменные, факты и приоритеты](../fundamentals/06-variables.md)
