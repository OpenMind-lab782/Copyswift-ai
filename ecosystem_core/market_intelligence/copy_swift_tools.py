"""Deterministic CopySwiftAI cross-tool recommendations for Ad Copy."""
TOOL_CATALOG={"ad-image":("🎨 Generate an Ad Image","Turn the winning ad idea into a visual creative with CopySwiftAI's AI image generator."),"image-enhancement":("✨ Enhance Your Original Product Image","Upload the real product photo to improve presentation while preserving the original product."),"talking-video":("🎙️ Turn the Ad Into a Talking Video","Use the winning ad as the speaking script for a short AI presenter video."),"animate-image":("🎬 Animate the Product Image","Turn a product image into a short motion video for social advertising."),"tiktok-script":("🎵 Create a Short-Form Video Script","Convert the campaign idea into a short video script with a hook, talking points and CTA."),"whatsapp":("💬 Reuse It as a WhatsApp Sales Message","Turn the winning ad into a conversational WhatsApp message with a direct response CTA."),"email":("📧 Reuse It as an Email Campaign","Expand the winning ad into a sales email with subject line, benefits and CTA."),"sms":("📱 Create an SMS Promo","Compress the campaign offer into a short SMS promo with a clear CTA."),"product-description":("🛒 Build a Product Description","Reuse the offer and customer-benefit language as a stronger product description.") }
def recommend_copy_swift_tools(offer="",customer="",hesitation="",platform="",tone="",product_url=""):
 text=" ".join(str(v).lower() for v in (offer,customer,hesitation,platform,tone) if v); ids=[]
 def add(x):
  if x not in ids: ids.append(x)
 add("ad-image")
 if product_url or any(w in text for w in ("photo","image","picture","product")): add("image-enhancement")
 add("talking-video")
 if any(w in text for w in ("instagram","facebook","video","reel","tiktok","social")): add("animate-image"); add("tiktok-script")
 if "whatsapp" in text or "status" in text: add("whatsapp")
 elif "email" in text: add("email")
 elif "sms" in text or "text message" in text: add("sms")
 else: add("whatsapp"); add("email")
 if any(w in text for w in ("product","service","course","property","package","offer")): add("product-description")
 return [{"id":i,"title":TOOL_CATALOG[i][0],"how":TOOL_CATALOG[i][1],"route":"/","cta":"Open CopySwiftAI"} for i in ids[:5]]
