 curl -X POST https://aceme.tech/api/v1/apartment -H "Content-Type: application/json" -d '{
  "address": "123 Main St",
  "description": "Spacious 2-bedroom apartment with a beautiful view",
  "apartment_type": "2-bedroom",
  "sales_exec": "John Doe",
  "apartment_pic": "http://example.com/image.jpg",
  "status": "available",
  "location": "Downtown",
  "price": 1500
}'
