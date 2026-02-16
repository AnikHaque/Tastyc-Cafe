import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class InvoiceGenerator:
    """পুরো পাইথন ক্লাস যা ইনভয়েস জেনারেট করার জটিল লজিক হ্যান্ডেল করে"""
    
    def __init__(self, order):
        self.order = order

    def generate(self):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # পাইথন ড্রয়িং লজিক
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, 750, "RoyalDine Receipt")
        
        p.setFont("Helvetica", 12)
        y = 700
        data = [
            f"Order ID: {self.order.id}",
            f"Date: {self.order.created_at.strftime('%Y-%m-%d')}",
            f"Customer: {self.order.full_name}",
            f"Amount: BDT {self.order.total_price}",
        ]
        
        for line in data:
            p.drawString(100, y, line)
            y -= 25
            
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer