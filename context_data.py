"""Original synthetic business folders and deterministic, private answer keys."""
import json
import random

SEED = 20261102
FAMILIES = ('refunds', 'bookings', 'invoices')


def document(ident, title, text):
    return {'id': ident, 'title': title, 'text': text}


def refund_answer(p):
    if p['age'] is None or p['condition'] is None:
        return 'clarify', None
    if p['condition'] == 'damaged' and p['age'] <= 7:
        if p['photos'] is None:
            return 'clarify', None
        if p['photos']:
            return 'approve', p['paid'] - p['shipping']
    window = p['override'] if p['override'] is not None else 45 if p['vip'] else 30
    if p['final'] or p['condition'] != 'unopened' or p['age'] > window:
        return 'decline', 0
    return 'approve', p['paid'] - p['shipping']


def booking_answer(p):
    if p['duration'] is None or p['travel'] is None:
        return 'clarify', None
    if p['required'] not in p['skills'] or not p['credential_valid']:
        return 'decline', 0
    for start, end in sorted(p['customer_windows']):
        earliest = max(start, p['shift'][0] + p['travel'])
        if p['break'] and earliest < p['break'][1] and earliest + p['duration'] > p['break'][0]:
            earliest = p['break'][1]
        if earliest + p['duration'] <= min(end, p['shift'][1]):
            return 'approve', earliest
    return 'decline', 0


def invoice_answer(p):
    if p['received'] is None or p['bank_verified'] is None:
        return 'clarify', None
    if p['duplicate'] or p['cancelled'] or not p['bank_verified']:
        return 'decline', 0
    if p['qty'] > p['received'] or p['unit'] > p['ceiling']:
        return 'decline', 0
    return 'approve', p['qty'] * p['unit'] + p['freight'] - p['credit']


def build():
    rng = random.Random(SEED)
    corpora, tasks = {}, []
    policies = {
        'refunds': ('Refund policy, revision 2026-10-01, CURRENT',
            'For decisions on 2026-11-02 this revision supersedes every earlier refund policy. '
            'Unopened items qualify within 30 days of delivery inclusive, or 45 days inclusive for VIP customers. '
            'An explicit account-specific return window overrides those two windows. Final-sale items and opened items do not qualify. '
            'Exception: damaged goods delivered at most 7 days ago qualify, even when final-sale, if damage photos are confirmed present. '
            'If damage photos are explicitly absent, the exception does not apply. If their presence is unknown, clarify. '
            'Missing delivery age or item condition requires clarification. Approved refund equals total paid minus shipping in integer cents. '
            'Never refund shipping. Decline value is 0; clarification value is null. Cite this policy and both account records.'),
        'bookings': ('Booking policy, revision 2026-10-01, CURRENT',
            'For decisions on 2026-11-02 use these rules, superseding every earlier booking policy. '
            'Find the earliest feasible start for the named technician today. They must hold the required skill and a currently valid credential. '
            'The entire job must fit inside one customer window and the technician shift. '
            'Travel happens at shift start, before the first job. Earliest arrival is shift start plus travel minutes. '
            'A job cannot overlap a scheduled break, but may end exactly when the break starts or start when it ends. '
            'If a tentative start overlaps a break, try starting at break end, then check the customer window and shift again. '
            'Missing duration or travel time requires clarification. Missing required skill or an expired credential requires decline. '
            'Approve value is start time in integer minutes after midnight; decline is 0; clarify is null. Cite this policy and both job records.'),
        'invoices': ('Invoice approval policy, revision 2026-10-01, CURRENT',
            'For decisions on 2026-11-02 use this revision, superseding all earlier invoice policies. '
            'Approve only if the invoice is not a duplicate, the purchase order is not cancelled, bank verification is confirmed, '
            'billed quantity is at most quantity received, and unit price is at most the signed contract ceiling. Equality is allowed. '
            'There is NO general price tolerance. A signed account-specific ceiling is authoritative. '
            'Missing received quantity or unknown bank verification requires clarification before other checks. '
            'An explicitly failed bank verification requires decline. '
            'Approved value is quantity times unit price, plus freight, minus credit, all in integer cents. '
            'Decline is 0; clarify is null. Cite this policy and both invoice records.'),
    }
    for family in FAMILIES:
        prefix = {'refunds': 'R', 'bookings': 'B', 'invoices': 'I'}[family]
        policy_id = prefix + '-POLICY'
        title, text = policies[family]
        docs = [document(policy_id, title, text)]
        docs += [document(prefix + '-OLD-' + str(k), 'ARCHIVED ' + family + ' policy, revision 2025-0' + str(k),
            'RETIRED. Not applicable to decisions on 2026-11-02. '
            + {'refunds': 'The old return window was 14 days and shipping was refundable. VIP had no exception.',
               'bookings': 'The old procedure allowed ignoring travel when making a tentative booking and allowed a job to run past shift end.',
               'invoices': 'The old procedure allowed a 5 percent unit-price tolerance and approved purchase orders before delivery.'}[family]) for k in (1, 2, 3)]
        for j in range(20):
            case = prefix + '-' + str(731 + j * 17)
            a, b = case + '-A', case + '-B'
            kind = j % 10
            if family == 'refunds':
                p = {'age': 12, 'condition': 'unopened', 'photos': False, 'vip': False,
                     'final': False, 'override': None, 'paid': rng.randrange(6000, 26000), 'shipping': rng.choice([350, 550, 850])}
                if kind == 1: p['age'] = 36
                if kind == 2: p.update(age=36, vip=True)
                if kind == 3: p.update(age=10, final=True)
                if kind == 4: p.update(age=5, condition='damaged', photos=None, final=True)
                if kind == 5: p.update(age=5, condition='damaged', photos=True, final=True)
                if kind == 6: p['age'] = None
                if kind == 7: p['age'] = 25
                if kind == 8: p.update(age=50, override=60)
                if kind == 9: p.update(age=30, condition='opened')
                order = {k: p[k] for k in ('age', 'condition', 'photos', 'paid', 'shipping')}
                account = {k: p[k] for k in ('vip', 'final', 'override')}
                atitle, btitle = 'Delivered order and refund request', 'Signed account terms and sale conditions'
                atext = 'Delivery age is days before 2026-11-02; null means not recorded. Item condition, confirmed damage photos, total paid cents, shipping cents: ' + json.dumps(order)
                btext = 'VIP membership, final-sale flag, account-specific return-window days (null means no override): ' + json.dumps(account)
                question = f'Decide the refund request for account {case} on 2026-11-02. Return the refund in cents if approved.'
                decision, value = refund_answer(p)
            elif family == 'bookings':
                p = {'duration': 50, 'travel': 25, 'required': 'electrical', 'skills': ['electrical', 'inspection'],
                     'credential_valid': True, 'shift': [540, 1020], 'customer_windows': [[570, 720], [840, 960]], 'break': [720, 750]}
                if kind == 1: p['skills'] = ['inspection']
                if kind == 2: p.update(customer_windows=[[540, 610]], duration=50, travel=25)
                if kind == 3: p.update(customer_windows=[[690, 810]], duration=60)
                if kind == 4: p['travel'] = None
                if kind == 5: p.update(customer_windows=[[990, 1080]], duration=40)
                if kind == 6: p['credential_valid'] = False
                if kind == 7: p.update(customer_windows=[[665, 720]], duration=55)
                if kind == 8: p.update(customer_windows=[[600, 630], [840, 900]], duration=50)
                if kind == 9: p['duration'] = None
                # Vary clock values while preserving relative constraints and boundaries.
                shift = rng.choice([-30, 0, 30])
                p['shift'] = [x + shift for x in p['shift']]
                p['customer_windows'] = [[x + shift for x in w] for w in p['customer_windows']]
                p['break'] = [x + shift for x in p['break']]
                atitle, btitle = 'Customer service job and requested windows', 'Assigned technician availability and credential record'
                atext = 'All clock values are integer minutes after midnight; windows are [start,end]. Job details: ' + json.dumps({k: p[k] for k in ('duration', 'required', 'customer_windows')})
                btext = 'All clock values are minutes after midnight; null means unknown. Technician record: ' + json.dumps({k: p[k] for k in ('travel', 'skills', 'credential_valid', 'shift', 'break')})
                question = f'Decide whether the assigned technician can take service job {case} today, 2026-11-02. If approved, return its earliest feasible start in minutes after midnight.'
                decision, value = booking_answer(p)
            else:
                p = {'qty': rng.randrange(3, 12), 'received': 20, 'unit': rng.randrange(800, 2000), 'ceiling': 2100,
                     'bank_verified': True, 'duplicate': False, 'cancelled': False, 'freight': 500, 'credit': 150}
                if kind == 1: p['duplicate'] = True
                if kind == 2: p['received'] = p['qty'] - 1
                if kind == 3: p['unit'] = 2150
                if kind == 4: p['received'] = None
                if kind == 5: p['bank_verified'] = None
                if kind == 6: p['cancelled'] = True
                if kind == 7: p.update(unit=2300, ceiling=2300)
                if kind == 8: p['bank_verified'] = False
                if kind == 9: p['received'] = p['qty']
                atitle, btitle = 'Vendor invoice submitted for payment', 'Receipt, signed contract and payment-control record'
                atext = 'Quantity, unit price cents, freight cents and credit cents: ' + json.dumps({k: p[k] for k in ('qty', 'unit', 'freight', 'credit')})
                btext = 'Received quantity, contract unit-price ceiling cents, bank verification, duplicate and cancellation checks; null means unknown: ' + json.dumps({k: p[k] for k in ('received', 'ceiling', 'bank_verified', 'duplicate', 'cancelled')})
                question = f'Decide whether vendor invoice {case} can be approved on 2026-11-02. If approved, return the payable total in cents.'
                decision, value = invoice_answer(p)
            docs.extend([document(a, case + ': ' + atitle, atext), document(b, case + ': ' + btitle, btext)])
            tasks.append({'id': case, 'family': family, 'split': 'development' if j < 4 else 'heldout',
                          'kind': kind, 'question': question, 'required_evidence': [policy_id, a, b],
                          'expected': {'decision': decision, 'value': value}, 'parameters': p})
        # Plausible background material, clearly scoped to unrelated accounts/projects.
        topics = ['inventory handover', 'staff training', 'supplier onboarding', 'website refresh', 'monthly planning',
                  'equipment inspection', 'new branch launch', 'customer feedback', 'warehouse labeling', 'team meeting']
        for k in range(80):
            ident = prefix + '-NOTE-' + str(k + 1).zfill(3)
            topic = topics[k % len(topics)]
            words = (f'Internal {family} operations note about {topic}, project P-{4000+k}. '
                     'This project does not change current customer terms or approval rules. '
                     f'The coordinator reviewed {11+k} records, scheduled a follow-up and requested confirmation from the local team. '
                     'The open items concern document ownership, archive naming, meeting availability, training attendance and handover responsibilities. '
                     'Draft suggestions require a signed policy revision before they can affect operational decisions. '
                     f'Budget discussion reference {9000+k}; next review 2026-12-{1+k%25:02d}. '
                     'Use the current policy and the named account records for an individual customer decision.')
            docs.append(document(ident, topic.capitalize() + ': unrelated project P-' + str(4000+k), words))
        random.Random(SEED + len(family)).shuffle(docs)
        corpora[family] = docs
    return corpora, tasks
