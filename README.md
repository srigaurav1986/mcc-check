# mcc-check

**MCC का संकेत, MDR का हिसाब और merchant audit।**

MCC (मर्चेंट कैटेगरी कोड) एक 4-अंकों का कोड है। यह तय करता है कि merchant से कितना शुल्क (MDR) लिया जाएगा। यह कोड merchant खुद नहीं चुनता, इसे acquirer या payment processor तय करता है। गलत MCC से merchant का सीधा नुकसान हो सकता है, इसलिए यह tool तीन काम करता है:

1. **लुकअप:** किसी MCC कोड का अर्थ देखें।
2. **संकेत:** merchant के नाम या narration से संभावित MCC सुझाएँ।
3. **Audit:** statement की जाँच करें कि कटा MDR नियम के अनुसार सही है या नहीं, और MCC की समीक्षा की ज़रूरत है या नहीं।

सब कुछ आपकी मशीन पर चलता है। इसमें कोई network call नहीं है और कोई बाहरी dependency नहीं है।

## शुरू करें

Python 3.9 या नया चाहिए।

```
python3 -m mcc_check lookup 5912
python3 -m mcc_check suggest "गुप्ता मेडिकल हॉल"
python3 -m mcc_check mdr --amount 5000 --instrument upi_p2m
python3 -m mcc_check audit examples/statement.csv --dispute
```

Tests चलाने के लिए:

```
python3 -m unittest discover -s tests -t .
```

## Statement फ़ाइल का फ़ॉर्मैट

CSV में ये कॉलम होने चाहिए:

| कॉलम | ज़रूरी | अर्थ |
|---|---|---|
| `date` | हाँ | `YYYY-MM-DD` |
| `amount` | हाँ | लेनदेन की रकम |
| `mdr_charged` | हाँ | जो MDR कटा |
| `merchant_name` | हाँ | merchant का नाम |
| `assigned_mcc` | हाँ | जो MCC assign हुआ |
| `instrument` | नहीं | जैसे `upi_p2m`, डिफ़ॉल्ट यही है |

## नियम कैसे बदलें

डिफ़ॉल्ट नियम एक बैंक की सूचना पर आधारित हैं, जिसमें सामान्य UPI P2M पर 0.40% तक शुल्क है, अधिकतम ₹300 प्रति लेनदेन, और ₹2,000 तक शून्य। नियम बदलने पर JSON फ़ाइल दें:

```json
{
  "upi_p2m": {"rate": "0.004", "cap": "300", "zero_below": "2000"},
  "rupay_cc_upi:5541": {"rate": "0.01", "cap": null, "zero_below": "0"}
}
```

`instrument:MCC` वाली कुंजी किसी खास MCC के लिए नियम देती है। इसे `--rules` से पास करें।

## यह tool क्या नहीं करता

- यह MCC नहीं बदलता, और merchant को MDR बचाने के लिए category बदलने की सलाह नहीं देता। MCC की अंतिम पुष्टि acquirer या payment service provider करता है।
- यह किसी बैंक या NPCI से जुड़ा नहीं है।
- यह कानूनी या वित्तीय सलाह नहीं है।
- MDR की दरें बैंक के अनुसार अलग हो सकती हैं, और नियम समय के साथ बदलते हैं। हर दर का स्रोत और तारीख जाँचें।

## Dispute draft

`--dispute` से हर OVERCHARGE और MCC_REVIEW मामले के लिए acquirer या NPCI को भेजने योग्य समीक्षा-अनुरोध का मसौदा मिलता है। यह केवल समीक्षा माँगता है, और अंतिम निर्णय acquirer या NPCI का होता है।

## डेटा की सीमा

MCC सूची ISO 18245 का एक प्रारंभिक उपसमुच्चय है, जिसमें भारतीय keywords जोड़े गए हैं। इसे उपयोग से पहले आधिकारिक सूची और अपने acquirer के दस्तावेज़ों से मिलाएँ। योगदान का स्वागत है, पर असली merchant का डेटा commit न करें।

## लाइसेंस

MIT। देखें [LICENSE](LICENSE)।
