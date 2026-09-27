# Приём заявок в Aspro Cloud

Статический Astro не должен содержать API-токены CRM. Используйте серверный HTTPS webhook (например, n8n на ZimaOS):

1. Создайте webhook POST /itgroup-lead с JSON. Ограничьте CORS разрешённым origin https://karpiev.ru; предусмотрите rate limiting, валидацию, антиспам и защиту от повторов.
2. Проверьте обязательные поля name, phone, consent, длину полей и пустой honeypot website. Не считайте клиентское поле consent достаточным юридическим основанием без актуальной политики.
3. В серверном workflow создайте контакт/сделку в Aspro Cloud через серверную авторизацию. Токены храните только в секретах n8n, не в GitHub и не в браузере.
4. Возвращайте HTTP 2xx только после успешного создания заявки в CRM, иначе код ошибки. Логируйте результат без раскрытия персональных данных.
5. Запишите HTTPS адрес webhook в astro/.env (PUBLIC_LEAD_ENDPOINT), затем пересоберите сайт. Не публикуйте форму, пока workflow и политика персональных данных не готовы.

Форма отправляет JSON: name, phone, messenger, company, project_type, description, budget, consent, source, page_url и UTM-поля. Вложения в текущей версии не поддерживаются.
