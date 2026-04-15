import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# =========================
# LOAD CSV (FLUX SAFE MODE)
# =========================
try:
    data = pd.read_csv("cnc_data.csv", skiprows=3)
except:
    data = pd.read_csv("cnc_data.csv")

print("Columns detected:", data.columns)

# Remove unnamed columns
data = data.loc[:, ~data.columns.str.contains("^Unnamed")]

# If _value column exists use it
if "_value" in data.columns:
    values = pd.to_numeric(data["_value"], errors="coerce").dropna().values
else:
    # Otherwise take last numeric column
    data_numeric = data.apply(pd.to_numeric, errors="coerce")
    data_numeric = data_numeric.dropna(axis=1, how="all")

    if data_numeric.shape[1] == 0:
        raise ValueError("No numeric data found in CSV!")

    values = data_numeric.iloc[:, -1].dropna().values

print("Total data points:", len(values))

if len(values) < 15:
    raise ValueError("Not enough data for training!")

# =========================
# NORMALIZE
# =========================
min_val = values.min()
max_val = values.max()

values = (values - min_val) / (max_val - min_val + 1e-8)

# =========================
# CREATE SEQUENCES
# =========================
def create_sequences(data, seq_len=10):
    xs, ys = [], []
    for i in range(len(data) - seq_len):
        xs.append(data[i:i+seq_len])
        ys.append(data[i+seq_len])
    return np.array(xs), np.array(ys)

SEQ_LEN = 10
X, y = create_sequences(values, SEQ_LEN)

# Convert to tensors
X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
y = torch.tensor(y, dtype=torch.float32)

# =========================
# MODEL
# =========================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=50, batch_first=True)
        self.fc = nn.Linear(50, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

model = LSTMModel()
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# =========================
# TRAIN
# =========================
epochs = 20

for epoch in range(epochs):
    model.train()
    pred = model(X)
    loss = loss_fn(pred.squeeze(), y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f}")

# =========================
# SAVE MODEL
# =========================
torch.save(model.state_dict(), "lstm_model.pth")
print("Model saved successfully!")

# =========================
# TEST PREDICTION
# =========================
model.eval()
with torch.no_grad():
    test = X[-1].unsqueeze(0)
    prediction = model(test)

    predicted_value = prediction.item() * (max_val - min_val) + min_val
    print("Next predicted value:", predicted_value)