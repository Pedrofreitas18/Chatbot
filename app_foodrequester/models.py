from django.db import models

class CardapioItem(models.Model):
    nome  = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nome} (R${self.preco})" 

class User(models.Model):
    name   = models.CharField(max_length=100)
    number = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.name} ({self.number})"

class Address(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    street        = models.CharField(max_length=100)
    number        = models.CharField(max_length=10)
    complement    = models.CharField(max_length=100, blank=True, null=True)
    neighborhood  = models.CharField(max_length=50)
    city          = models.CharField(max_length=50)
    state         = models.CharField(max_length=2)
    zip_code      = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.neighborhood}, {self.city}/{self.state}"

class MessageHistory(models.Model):
    sender = models.CharField(max_length=10, choices=[("user", "User"), ("bot", "Bot")])
    user_number = models.CharField(max_length=15)  # pode ser o número de telefone
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.sender} - {self.message[:30]}"
    
def get_last_messages(user_number, limit=5):
    messages = MessageHistory.objects.filter(user_number=user_number).order_by('-timestamp')[:limit]
    return "\n".join(
        f"{m.sender}: {m.message}" for m in reversed(messages)
    )