import typing

from django.utils import timezone


class CooldownMixin:
    def __init__(self, threshold: int, amount: timezone.timedelta):
        # threshold to take cd_until into consideration
        self.threshold = threshold
        # if equals to cd_threshold, check cd_until: if past, reset count, if not, prevent things from happening
        self.current_count = 0
        # cooldown to avoid discord anti-spam
        self.amount = amount
        self.until: typing.Optional[timezone.datetime] = None

    def check(self) -> bool:
        if self.current_count >= self.threshold:
            now = timezone.now()
            # cooldown is over
            if self.until < now:
                # reset count, cooldown
                self.until = now + self.amount
                self.current_count = 1
                return True
            # on cooldown
            else:
                return False
        else:
            # first initialization
            if self.current_count == 0:
                self.until = timezone.now() + self.amount
            self.current_count += 1
            return True
