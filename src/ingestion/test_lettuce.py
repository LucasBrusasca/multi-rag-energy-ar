import torch
torch.set_num_threads(1)

from lettucedetect.models.inference import HallucinationDetector

detector = HallucinationDetector(
    method = "transformer",
    model_path = "KRLabsOrg/lettucedect-v2-mmbert-base"
    )

contexto = (
        "Quedan sujetos a retención los importes correspondientes a los conceptos del Anexo II "
        "de la RG 830, siempre que correspondan a beneficiarios del pais no exentos ni excluidos "
        "del impuesto. No corresponde retener cuando el beneficiario obtuvo un certificado de exclusión."
    )
pregunta = "Que retención del impuesto a las ganancias tengo que aplicar?"

respuesta = (
    "Se retiene a los beneficiarios del pais no exentos por los conceptos del Anexo II. "
    "La alicuota aplicable es del 6% sobre el total facturado."
)

spans_1 = detector.predict(context=[contexto],
question=pregunta, answer=respuesta, output_format= "spans")
spans_2 = detector.predict(context=[contexto],
question=pregunta, answer=respuesta, output_format= "spans")

print("== corrida 1 ==")
for s in spans_1:
    print(f" No respaldado: '{s['text']}' (conf {s['confidence']:.3f})")
print("== corrida 2 ==")
for s in spans_2:
    print(f" No respaldado: '{s['text']}' (conf {s['confidence']:.3f})")

print(f"\nDETERMINISMO (mismo input -> misma salida): {spans_1 == spans_2}")