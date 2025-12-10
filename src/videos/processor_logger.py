from proglog import ProgressBarLogger

from src.settings import config


class ProcessorLogger(ProgressBarLogger):
    def callback(self, **changes):
        for (parameter, value) in changes.items():
            if parameter == 'message':
                print(f"LOG MESSAGE: {value}")

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar in self.bars:
            total = self.bars[bar]['total']

            if total > 0:
                percentage = (value / total) * 100
                print(f"Rendering Progress: {percentage:.1f}% completed")
