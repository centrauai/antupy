"""
Custom DataFrame with unit tracking functionality.
"""

from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import polars as pl
from typing import Dict, List, Any, overload, Literal, Self, Sequence, TypeAlias

from antupy.core.units import Unit
from antupy.core.var import Var
from antupy.core.array import Array

FrameInput: TypeAlias = pl.DataFrame | pd.DataFrame | dict[str, Any] | np.ndarray | Sequence | None


class Frame():

    def __init__(
            self,
            _data: FrameInput | Frame | None = None,
            _units: dict[str, str] | None = None
    ):
        if isinstance(_data, Frame):
            self.data = _data.df("pl")
            self.units = _data.units
        elif isinstance(_data, (pl.DataFrame, pd.DataFrame, dict, np.ndarray)):
            self.data = pl.DataFrame(_data)
            if _units is not None:
                self.units = {k:Unit(v) for k, v in _units.items()}
            else:
                self.units = {k: Unit("-") for k in self.data.columns}
        else:
            raise TypeError("data must be a Frame, pl.DataFrame, pd.DataFrame, dict, or None")

    def __add__(self, other: Frame) -> Frame:
        if not isinstance(other, Frame):
            raise TypeError("Can only add Frame to Frame")

        for col in self.data.columns:
            unit1 = self.units.get(col, Unit("-"))
            unit2 = other.units.get(col, Unit("-"))
            if unit1 and unit2 and unit1 != unit2:
                raise ValueError(f"Units in col {col} are not compatible: '{unit1}' and '{unit2}'")
        return Frame(self.data + other.gv(self.u), self.u)
    
    def __mul__(
            self, other: Var | Array | Frame
    ) -> Frame:
        
        if isinstance(other, (Var, Array)):
            return Frame(self.data * other.v, )
        elif isinstance(other, Frame):
            pass
        else:
            raise TypeError("Can only multiply Frame by Var, Array, or Frame")

    def __len__(self) -> int:
        return len(self.data)
    
    @overload
    def __getitem__(self, key: str) -> Array: ...

    @overload
    def __getitem__(self, key: list[str]) -> Frame: ...

    def __getitem__(
            self,
            key: str | list[str] | None = None
        ) -> Array | Frame:
        if isinstance(key, str):
            if key not in self.data.columns:
                raise KeyError(f"Column '{key}' not found in Frame")
            unit = self.units.get(key, "")
            values = self.data[key].to_numpy()
            return Array(values, unit)
        elif isinstance(key, list):
            return Frame(self.data.select(key), {k: self.u[k] for k in key})
        elif key is None:
            return self
        else:
            raise TypeError("key must be a string, list of strings, or None")

    @property
    def v(self) -> pl.DataFrame:
        """Return the underlying DataFrame."""
        return self.data

    @property
    def u(self) -> dict[str, str]:
        """Return the units dictionary."""
        return {k: v.label_unit for k, v in self.units.items()}
    
    @overload
    def df(self, _type: Literal["pl"]) -> pl.DataFrame: ...

    @overload
    def df(self, _type: Literal["pd"]) -> pd.DataFrame: ...

    def df(self, _type: Literal["pl", "pd"] = "pl") -> pl.DataFrame | pd.DataFrame:
        """Return the underlying DataFrame."""
        if _type == "pl":
            return self.data
        elif _type == "pd":
            return self.data.to_pandas()
        else:
            raise ValueError("Invalid type specified. Use 'pl' or 'pd'. Default is pl.")


    def get_value(
        self,
        cols: str | list[str] | dict[str, str] | None = None
    ) -> pl.DataFrame | pl.Series:
        if cols is None:
            return self.v
        elif isinstance(cols, str):
            return self.v[cols]
        elif isinstance(cols, list):
            return self.v.select(cols)
        elif isinstance(cols, dict):
            return self.v.select(cols.keys())
        else:
            raise TypeError("cols must be a string, list of strings, dict, or None")


    # just placeholder for now
    def set_units(
            self,
            units: dict[str, str] | list[str]
    ) -> Self:
        pass
        return self

    def gv(
            self,
            cols: str | list[str] | dict[str, str] | None = None
    ) -> pl.DataFrame | pl.Series:
        return self.get_value(cols)

    def su(
            self,
            units: dict[str, str] | list[str]
    ) -> Self:
        return self.set_units(units)

    @property
    def columns(self) -> list[str]:
        """Return the list of column names."""
        return self.data.columns
     

def main():

    pass

if __name__ == "__main__":
    main()