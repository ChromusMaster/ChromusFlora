# English

Delivery revision: **Fix 1**, 2026-09-25.

The previously delivered ZIP was found to be incomplete: the local copy and
its persisted download lacked the ZIP central directory/end record. The
previous delivery's integrity claim therefore did not hold for the artifact
received. No cause is attributed to the user's extraction software.

The bootstrap also required Get-FileHash, which was unavailable in the user's
PowerShell session. The corrected bootstrap uses SHA256.Create/ComputeHash
and ZipFile.ExtractToDirectory from .NET. It does not call Get-FileHash or
Expand-Archive. Downloads are verified before promotion from .part; invalid
cached downloads are replaced. Extraction is staged and only a completed,
verified distribution receives a completion marker. A bootstrap lock prevents
simultaneous extraction in this project's cache. The global Gradle cache is
not removed.

Validation performed: PowerShell 7.6.6 on Linux, using synthetic ZIP fixtures
and deliberately failing substitutes for the two unavailable cmdlets. Tests
passed for PowerShell syntax, absence of internal PowerShell comments, the
SHA-256 test vector "abc", ZIP extraction, replacing an incomplete extraction,
rejecting a wrong SHA-256, rejecting malformed ZIP data, cleaning temporary
folders and preserving a previous installation when staging fails.

The complete active source/resource scan is repeated for this correction.
The replacement ZIP uses the standard STORE method, with no compression.
It is closed and atomically renamed before independent ZIP/CRC checks,
extraction and source-manifest verification. The persisted download is then
retrieved and validated again before the user-facing link is returned.

No Java compilation, Gradle invocation, Minecraft execution or Windows runtime
test was performed. Those checks remain pending. The isolated PowerShell
bootstrap tests do not establish mod runtime compatibility.

After extracting the complete replacement over the repository root, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat clean build --warning-mode=fail
```

The first command detects missing files and mismatches against the delivery
manifest. Intentional local changes also produce mismatches. Use JDK 25 for
the build. Do not proceed if extraction reports ZIP errors.

# Português do Brasil

Revisão da entrega: **Fix 1**, 25/09/2026.

O ZIP entregue anteriormente estava incompleto: tanto a cópia local quanto
a cópia recuperada para download não continham o índice central/registro final
do ZIP. Portanto, a afirmação anterior de integridade não se confirmou para
o artefato recebido. Não se atribui a causa ao extrator utilizado pelo usuário.

O inicializador também dependia de Get-FileHash, indisponível na sessão
PowerShell do usuário. A correção usa SHA256.Create/ComputeHash e
ZipFile.ExtractToDirectory do .NET, sem chamar Get-FileHash ou Expand-Archive.
Downloads são verificados antes de saírem do arquivo .part; downloads inválidos
no cache são substituídos. A extração ocorre em pasta temporária e só recebe
marcador de conclusão após verificação e extração completas. Um bloqueio do
inicializador impede extrações simultâneas no cache deste projeto. O cache
global do Gradle não é apagado.

Validação executada: PowerShell 7.6.6 no Linux, com ZIPs de teste e substitutos
que falham se os cmdlets indisponíveis forem chamados. Passaram: sintaxe
PowerShell, ausência de comentários internos nos scripts, vetor SHA-256 "abc",
extração, substituição de extração incompleta, rejeição de hash incorreto,
rejeição de ZIP malformado, limpeza temporária e preservação da instalação
anterior quando a preparação da nova extração falha.

O scan global dos fontes/recursos ativos é repetido. O ZIP substituto usa
STORE, sem compressão, e é fechado e renomeado atomicamente antes da conferência
independente de ZIP/CRC, extração e comparação com o manifesto dos fontes.
A cópia disponibilizada é recuperada e validada novamente antes do envio do link.

Não houve compilação Java, chamada do Gradle, execução do Minecraft ou teste
em Windows. Esses testes continuam pendentes. Os testes isolados do script
PowerShell não comprovam compatibilidade do mod em execução.

Extraia o pacote completo atualizado por cima da raiz do repositório e execute:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat clean build --warning-mode=fail
```

O primeiro comando detecta arquivos ausentes e divergências no manifesto.
Alterações locais intencionais também produzem divergências. Use JDK 25 para
compilar. Não prossiga se a extração informar erros de ZIP.
