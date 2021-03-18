#
# Test the base experiment class
#
import pybamm
import numpy
import unittest
import pandas as pd
import os


class TestExperiment(unittest.TestCase):
    def test_read_strings(self):
        # Import drive cycle from file
        drive_cycle = pd.read_csv(
            pybamm.get_parameters_filepath(
                os.path.join("input", "drive_cycles", "US06.csv")
            ),
            comment="#",
            header=None,
        ).to_numpy()

        experiment = pybamm.Experiment(
            [
                "Discharge at 1C for 0.5 hours",
                "Discharge at C/20 for 0.5 hours",
                "Charge at 0.5 C for 45 minutes",
                "Discharge at 1 A for 0.5 hours",
                "Charge at 200 mA for 45 minutes (1 minute period)",
                "Discharge at 1W for 0.5 hours",
                "Charge at 200 mW for 45 minutes",
                "Rest for 10 minutes (5 minute period)",
                "Hold at 1V for 20 seconds",
                "Charge at 1 C until 4.1V",
                "Hold at 4.1 V until 50mA",
                "Hold at 3V until C/50",
                "Discharge at C/3 for 2 hours or until 2.5 V",
                "Run US06",
                "Run US06 for 5 minutes",
                "Run US06 for 0.5 hours",
            ],
            {"test": "test"}, drive_cycles={"US06": drive_cycle},
            period="20 seconds",
        )
        
        # Calculation for operating conditions of drive cycle
        time_0 = drive_cycle[:, 0][-1]
        period_0 = numpy.min(numpy.diff(drive_cycle[:, 0]))
        drive_cycle_1 = experiment.extend_drive_cycle(
            drive_cycle, end_time= 300)
        time_1 = drive_cycle_1[:, 0][-1]
        period_1 = numpy.min(numpy.diff(drive_cycle_1[:, 0]))
        drive_cycle_2 = experiment.extend_drive_cycle(
            drive_cycle, end_time=1800)
        time_2 = drive_cycle_2[:, 0][-1]
        period_2 = numpy.min(numpy.diff(drive_cycle_2[:, 0]))

        self.assertEqual(
            experiment.operating_conditions[:-3],
            [
                (1, "C", 1800.0, 20.0),
                (0.05, "C", 1800.0, 20.0),
                (-0.5, "C", 2700.0, 20.0),
                (1, "A", 1800.0, 20.0),
                (-0.2, "A", 2700.0, 60.0),
                (1, "W", 1800.0, 20.0),
                (-0.2, "W", 2700.0, 20.0),
                (0, "A", 600.0, 300.0),
                (1, "V", 20.0, 20.0),
                (-1, "C", None, 20.0),
                (4.1, "V", None, 20.0),
                (3, "V", None, 20.0),
                (1 / 3, "C", 7200.0, 20.0),
            ],
        )
        # Check drive cycle operating conditions
        self.assertTrue(
            ((experiment.operating_conditions[-3][0] == drive_cycle[:, 1]).all() & (
                experiment.operating_conditions[-3][1] == "Drive") & (
                experiment.operating_conditions[-3][2] == time_0).all() & (
                experiment.operating_conditions[-3][3] == period_0).all() & (
                experiment.operating_conditions[-2][0] == drive_cycle_1[:, 1]).all() & (
                experiment.operating_conditions[-2][1] == "Drive") & (
                experiment.operating_conditions[-2][2] == time_1).all() & (
                experiment.operating_conditions[-2][3] == period_1).all() & (
                experiment.operating_conditions[-1][0] == drive_cycle_2[:, 1]).all() & (
                experiment.operating_conditions[-1][1] == "Drive") & (
                experiment.operating_conditions[-1][2] == time_2).all() & (
                experiment.operating_conditions[-1][3] == period_2).all())
        )
        self.assertEqual(
            experiment.events,
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (4.1, "V"),
                (0.05, "A"),
                (0.02, "C"),
                (2.5, "V"),
                None,
                None,
                None,
            ],
        )
        self.assertEqual(experiment.parameters, {"test": "test"})
        self.assertEqual(experiment.period, 20)

    def test_read_strings_repeat(self):
        experiment = pybamm.Experiment(
            ["Discharge at 10 mA for 0.5 hours"]
            + ["Charge at 0.5 C for 45 minutes", "Hold at 1 V for 20 seconds"] * 2
        )
        self.assertEqual(
            experiment.operating_conditions,
            [
                (0.01, "A", 1800.0, 60),
                (-0.5, "C", 2700.0, 60),
                (1, "V", 20.0, 60),
                (-0.5, "C", 2700.0, 60),
                (1, "V", 20.0, 60),
            ],
        )
        self.assertEqual(experiment.period, 60)

    def test_cycle_unpacking(self):
        experiment = pybamm.Experiment(
            [
                ("Discharge at C/20 for 0.5 hours", "Charge at C/5 for 45 minutes"),
                ("Discharge at C/20 for 0.5 hours"),
                "Charge at C/5 for 45 minutes",
            ]
        )
        self.assertEqual(
            experiment.operating_conditions,
            [
                (0.05, "C", 1800.0, 60.0),
                (-0.2, "C", 2700.0, 60.0),
                (0.05, "C", 1800.0, 60.0),
                (-0.2, "C", 2700.0, 60.0),
            ],
        )
        self.assertEqual(experiment.cycle_lengths, [2, 1, 1])

    def test_str_repr(self):
        conds = ["Discharge at 1 C for 20 seconds", "Charge at 0.5 W for 10 minutes"]
        experiment = pybamm.Experiment(conds)
        self.assertEqual(str(experiment), str(conds))
        self.assertEqual(
            repr(experiment),
            "pybamm.Experiment(['Discharge at 1 C for 20 seconds'"
            + ", 'Charge at 0.5 W for 10 minutes'])",
        )

    def test_bad_strings(self):
        with self.assertRaisesRegex(
            TypeError, "Operating conditions should be strings or tuples of strings"
        ):
            pybamm.Experiment([1, 2, 3])
        with self.assertRaisesRegex(
            TypeError, "Operating conditions should be strings or tuples of strings"
        ):
            pybamm.Experiment([(1, 2, 3)])
        with self.assertRaisesRegex(ValueError, "Operating conditions must contain"):
            pybamm.Experiment(["Discharge at 1 A at 2 hours"])
        with self.assertRaisesRegex(ValueError, "Instruction must be"):
            pybamm.Experiment(["Run at 1 A for 2 hours"])
        with self.assertRaisesRegex(
            ValueError, "Instruction must be"
        ):
            pybamm.Experiment(["Run at at 1 A for 2 hours"])
        with self.assertRaisesRegex(ValueError, "units must be"):
            pybamm.Experiment(["Discharge at 1 B for 2 hours"])
        with self.assertRaisesRegex(ValueError, "time units must be"):
            pybamm.Experiment(["Discharge at 1 A for 2 years"])
        with self.assertRaisesRegex(
            TypeError, "experimental parameters should be a dictionary"
        ):
            pybamm.Experiment([], "not a dictionary")


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    pybamm.settings.debug_mode = True
    unittest.main()
