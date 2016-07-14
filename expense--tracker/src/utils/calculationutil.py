class CalculationUtil(object):
    @staticmethod
    def calculateSummaryForAll(members, expenses):
        summary = {m.key:0 for m in members}
        for expense in expenses:
            payer = expense.paid_by
            summary[payer] -= expense.amount
            for ia in expense.individual_amount:
                summary[ia.user_key] += ia.amount
        return summary

    @staticmethod
    def calculateSummaryForUser(user, expenses):
        totalPaid = 0
        totalSpent = 0
        for expense in expenses:
            if expense.paid_by == user.key:
                totalPaid += expense.amount
            amount = expense.getAmountForUser(user)
            totalSpent += (0 if amount is None else amount)
        return totalPaid, totalSpent