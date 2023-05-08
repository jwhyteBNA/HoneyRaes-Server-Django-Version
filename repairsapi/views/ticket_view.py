"""View module for handling requests for customer data"""
# from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from django.db.models import Q
from repairsapi.models import ServiceTicket, Employee, Customer



class ServiceTicketView(ViewSet):
    """Honey Rae API customers view"""

    def create(self, request):
        """Handle POST requests for user tickets

        Returns:
            Response: JSON serialized representation of newly created service tickets
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


    def list(self, request):
        """Handle GET requests to get all service tickets

        Returns:
            Response -- JSON serialized list of service tickets
        """

        service_tickets = []

        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        if "status" in request.query_params:
            if request.query_params['status'] == "done":
                service_tickets = service_tickets.filter(date_completed__isnull=False)
            elif request.query_params['status'] == "unclaimed":
                service_tickets = service_tickets.filter(employee_id__isnull=True)
            elif request.query_params['status'] == "inprogress":
                service_tickets = service_tickets.filter(date_completed__isnull=True, employee_id__isnull=False)

        if "q" in request.query_params:
            searched_term = request.query_params['q']
            service_tickets = ServiceTicket.objects.filter(
                Q(description__contains=searched_term))

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer

        Returns:
            Response -- JSON serialized customer record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(service_ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for single ticket

        Returns:
            Response -- None with 204 status code
        """
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


    def update(self, request, pk=None):
        """Handle PUT requests for single customer
        
        Returns:
            Response -- No response body, just 204 status code.
        """

        #Select targeted ticket using PK
        ticket = ServiceTicket.objects.get(pk=pk)
        #Get the employee Id from the client request
        employee_id = request.data['employee']
        #Select the employee from the database using the Id
        assigned_employee = Employee.objects.get(pk=employee_id)
        #Assign that employee instance to the employee property of the ticket
        ticket.date_completed = request.data['date_completed']
        ticket.employee = assigned_employee
        #Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

class TicketEmployeeSerializer(serializers.ModelSerializer):
    """JSON serializer for employees"""
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name', )

class TicketCustomerSerializer(serializers.ModelSerializer):
    """JSON serializer for customers"""
    class Meta:
        model = Customer
        fields = ('id', 'user', 'address', 'full_name', )

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for customers"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'description', 'emergency', 'date_completed', 'customer', 'employee', )
        depth = 1
