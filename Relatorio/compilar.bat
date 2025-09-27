@echo off
echo Limpando builds anteriores...
rmdir /s /q build > nul 2>&1
rmdir /s /q dist > nul 2>&1

echo Recompilando o executável...
pyinstaller --noconfirm especificacao.spec

if exist "dist\Relatórios.exe" (
    echo.
    echo Compilacao concluida com sucesso!
    echo Executavel: dist\SistemaGestaoPropostas.exe
    timeout /t 3
) else (
    echo.
    echo ERRO na compilacao! Verifique as mensagens acima.
    pause
)