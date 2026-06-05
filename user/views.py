from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib import messages
from .models import PrintOrder, UserDetail
import razorpay
from django.http import JsonResponse 
from django.conf import settings
from django.core.mail import send_mail

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.
def profile(request):
    user_detail = UserDetail.objects.get(user=request.user)  # Fetch user details
    return render(request, 'profile.html', {'user_detail': user_detail})

def update_profile(request):
    if request.method == "POST":
        user_detail, created = UserDetail.objects.get_or_create(user=request.user)
        
        # Update phone and address
        user_detail.phone = request.POST.get('phone')
        user_detail.address = request.POST.get('address')
        user_detail.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return redirect('profile')

def list_orders(request):
    user_orders = PrintOrder.objects.filter(user=request.user).order_by('-order_date')  # Fetch orders
    return render(request, 'list_orders.html', {'user_orders': user_orders})

def order(request):
    return render(request, 'order.html')

def process_order(request):
    if request.user.is_anonymous:
        messages.error(request, 'You need to be logged in to place an order!')
        return redirect('signin')

    if request.method == 'POST':
        user_instance = request.user
        uploaded_file = request.FILES['file']
        print_type = request.POST['print-type']
        paper_size = request.POST['paper-size']
        copies = int(request.POST['copies'])
        notes = request.POST.get('notes', '')
        payment_mode = request.POST['payment-mode']

        base_price = {
            "black-white": 1.5,
            "color": 5.0
        }

        paper_multiplier = {
            "A4": 1.0,
            "A3": 1.5,
            "Letter": 1.2,
            "Legal": 1.3
        }

        print_cost = base_price.get(print_type, 0.10)
        paper_cost = paper_multiplier.get(paper_size, 1.0)
        file_size_mb = uploaded_file.size / 1024 / 1024  
        file_cost = file_size_mb * 1.0

        total_price = ((print_cost * paper_cost) + file_cost) * copies
        total_price = round(total_price, 2)  

        order = PrintOrder(
            user=user_instance,
            file=uploaded_file,
            print_type=print_type,
            paper_size=paper_size,
            copies=copies,
            notes=notes,
            total_amount=total_price,
            order_status='Pending'
        )
        order.save()

        subject = 'PrintEase: Your Order Has Been Received!'
        message = (
            f"Hello {user_instance.username},\n\n"
            f"Your order has been successfully placed!\n\n"
            f"📄 File Name: {uploaded_file.name}\n"
            f"🖨️ Print Type: {print_type}\n"
            f"📏 Paper Size: {paper_size}\n"
            f"📝 Copies: {copies}\n"
            f"📝 Notes: {notes}\n"
            f"💰 Total Price: ₹{total_price}\n"
            f"🆔 Order ID: {order.id}\n"
            f"💳 Payment Mode: {payment_mode}\n\n"
            f"Thank you for choosing PrintEase!\n\n"
            f"Best Regards,\nPrintEase Team"
        )
        email_from = settings.EMAIL_HOST_USER
        to_list = [user_instance.email]
        send_mail(subject, message, email_from, to_list)

        if payment_mode == 'cod':
            return render(request, 'order_success.html', {
                'file_name': uploaded_file.name,
                'print_type': print_type,
                'paper_size': paper_size,
                'copies': copies,
                'notes': notes,
                'total_price': total_price,
            })

        razorpay_order = razorpay_client.order.create({
            "amount": int(total_price * 100),
            "currency": "INR",
            "payment_capture": "1"
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "amount": total_price,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
            "callback_url": "/payment_success/",
            "order_db_id": order.id
        })
        
    
    return redirect('order')

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')

    order = get_object_or_404(PrintOrder, razorpay_order_id=order_id)
    order.razorpay_payment_id = payment_id
    order.payment_status = "Paid"
    order.save()

    messages.success(request, "Payment Successful! Your order has been placed.")
    return render(request, 'order_success.html', {
        'file_name': order.file.name,
        'print_type': order.print_type,
        'paper_size': order.paper_size,
        'copies': order.copies,
        'notes': order.notes,
        'total_price': order.total_amount,
    })

def order_success(request):
    return render(request, 'order_success.html')

def cancel_order(request, order_id):
    order = PrintOrder.objects.get(id=order_id)
    print(order.order_status)

    if order.order_status == "Processing":
        messages.error(request, "This order is already processing and cannot be canceled.")
        return redirect('list_orders')

    order.order_status = "Cancelled"  
    order.save()
    
    messages.success(request, "Order has been canceled successfully.")
    return redirect('list_orders')