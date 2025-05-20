#!/bin/bash

set -e

echo -e "\033[1;33mОстановка и удаление контейнеров...\033[0m"
cd bot && docker compose down -v --remove-orphans
echo -e "\033[1;31mКонтейнеры остановлены и удалены!\033[0m"