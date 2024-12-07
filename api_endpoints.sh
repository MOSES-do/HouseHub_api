 curl -X POST https://aceme.tech/api/v1/apartment -H "Content-Type: application/json" -d '{
  "address": "123 Main St",
  "description": "Spacious 2-bedroom apartment with a beautiful view",
  "apartment_type": "2-bedroom",
  "sales_exec": "John Doe",
  "apartment_pic": "https://plus.unsplash.com/premium_photo-1664266386277-2789b93c8b53?q=80&w=1935&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
  "status": "available",
  "location": "Downtown",
  "price": 1500
}'
