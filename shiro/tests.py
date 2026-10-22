from django.test import TestCase
from django.urls import reverse

from .models import ChangeRequest, Incident


class TicketIdFormTests(TestCase):
    def test_incident_ticket_id_can_be_entered_and_saved(self):
        response = self.client.get(reverse('shiro:incident_create'))
        self.assertNotIn('readonly', response.context['form']['ticket_id'].as_widget())

        response = self.client.post(
            reverse('shiro:incident_create'),
            {
                'ticket_id': 'INC0001234',
                'title': 'Network outage',
                'description': 'Office network is unavailable.',
                'status': 'new',
                'urgency': 'medium',
                'impact': 'low',
                'priority': 'medium',
                'reported_by': 'Test User',
            },
            follow=True,
        )

        incident = Incident.objects.get(ticket_id='INC0001234')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, incident.ticket_id)
        self.assertContains(response, incident.title)

    def test_crq_ticket_id_can_be_entered_and_saved(self):
        response = self.client.get(reverse('shiro:crq_create'))
        self.assertNotIn('readonly', response.context['form']['ticket_id'].as_widget())

        response = self.client.post(
            reverse('shiro:crq_create'),
            {
                'ticket_id': 'CHG0001234',
                'title': 'Network maintenance',
                'description': 'Upgrade network equipment.',
                'status': 'draft',
                'crq_type': 'standard',
                'risk_level': 'medium',
                'priority': 'medium',
                'requested_by': 'Test User',
            },
            follow=True,
        )

        crq = ChangeRequest.objects.get(ticket_id='CHG0001234')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, crq.ticket_id)
        self.assertContains(response, crq.title)
