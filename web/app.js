const form = document.getElementById("invoice-form");
const statusNode = document.getElementById("status");
const resultNode = document.getElementById("result");

function isoFromLocal(value) {
  return `${value}:00Z`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const payload = {
    invoice_ref: data.get("invoice_ref"),
    buyer: data.get("buyer"),
    supplier: data.get("supplier"),
    amount_minor: Number(data.get("amount_minor")),
    currency: data.get("currency"),
    delivery_deadline: isoFromLocal(data.get("delivery_deadline")),
  };

  statusNode.textContent = "Creating synthetic testnet instruction…";
  resultNode.textContent = "—";
  try {
    const response = await fetch("/v1/invoice-jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || "Request failed");
    statusNode.textContent = `Instruction ${body.status}`;
    resultNode.textContent = JSON.stringify(body, null, 2);
  } catch (error) {
    statusNode.textContent = `Could not create instruction: ${error.message}`;
  }
});
