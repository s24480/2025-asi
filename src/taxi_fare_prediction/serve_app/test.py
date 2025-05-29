from gradio_app import predict_fare

# Zastąp „Chotomów” i „Warszawa” na dowolne dwa adresy, które próbujesz
out = predict_fare(1, "Chotomów, Polska", "Warszawa, Polska", "card")
print("RESULT:", out)
