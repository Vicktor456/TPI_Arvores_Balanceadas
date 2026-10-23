from dataclasses import dataclass


@dataclass
class Aluno:
    matricula: int
    nome: str
    curso: str
    periodo: int

    def __post_init__(self) -> None:
        if isinstance(self.matricula, bool) or not isinstance(self.matricula, int):
            raise TypeError("A matrícula deve ser um número inteiro.")

        if self.matricula <= 0:
            raise ValueError("A matrícula deve ser um número positivo.")
