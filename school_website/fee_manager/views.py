from django.shortcuts import render
from django.http import HttpResponse
from weasyprint import HTML

def bill_input(request):
    """
    Render the bill input form.
    """
    return render(request, 'bill_input.html')


import base64

from django.template.loader import render_to_string

def generate_bill(request):
    """
    Generate the bill PDF and display it in a frame.
    """
    if request.method == 'POST':
        # Get input data from the form
        name = request.POST.get('name')
        usn = request.POST.get('usn')
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        fee_due = request.POST.get('fee_due')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id', None)
        receiver = request.POST.get('receiver', None)

        # Context for the bill template
        context = {
            'name': name,
            'usn': usn,
            'date': date,
            'amount': amount,
            'fee_due': fee_due,
            'payment_mode': payment_mode,
            'transaction_id': transaction_id,
            'receiver': receiver,
        }

        # Render the HTML bill template as a string
        html_template = render_to_string('bill_template.html', context)

        # Generate PDF from the HTML
        pdf_file = HTML(string=html_template).write_pdf()

        # Encode the PDF to a base64 string
        pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')

        # Save the base64 PDF string in the session
        request.session['pdf_file'] = pdf_base64

        # Redirect to the bill preview page
        return render(request, 'bill_preview.html')

    return HttpResponse("Invalid Request")

def download_bill(request):
    """
    Serve the generated bill PDF for download.
    """
    pdf_file = request.session.get('pdf_file')
    if pdf_file:
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bill.pdf"'
        return response
    return HttpResponse("No bill found. Please generate a bill first.")