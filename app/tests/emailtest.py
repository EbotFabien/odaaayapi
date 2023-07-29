from postmarker.core import PostmarkClient
postmark = PostmarkClient(server_token='9be26bfe-05d9-4780-bdf3-62d91c208f06')
postmark.emails.send(
  From='admin@odaaay.com',
  To='hello@odaaay.com',
  Subject='Postmark test',
  HtmlBody='Testing odaaay email service'
)

