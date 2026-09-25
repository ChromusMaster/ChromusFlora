# English

Revision: **Fix 2**, 2026-09-25.

The user's build reached compileJava and failed because Gson 2.14.0's
GsonBuilder.class references com.google.errorprone.annotations.InlineMe,
which was absent from the compilation classpath. Javac reported missing
replacement()/imports() annotation members, and -Werror stopped compilation.

The source fix adds error_prone_annotations 2.50.0 as compileOnly and
clientCompileOnly. Maven Central metadata was consulted; 2.50.0 was the latest
stable numeric release listed at review. Gson 2.14.0's published POM declares
2.48.0; the selected newer release retains the required annotation methods.
The published 2.50.0 jar was inspected directly: InlineMe is an annotation
with replacement(): String, imports(): String[] and staticImports(): String[].
Artifact URL and SHA-256 are recorded in dependency-fix2.json.

The compiler's -Xlint:all and -Werror flags and Gradle's warning.mode=fail
setting are unchanged. This adds neither an annotation processor nor a runtime
mod. No downloaded dependency jar is included in the source package.

Validation for this delivery includes the global offline scan, annotation
class/signature inspection, source-manifest verification, independent ZIP/CRC
checks and checking the persisted download against the pre-upload SHA-256.
The complete package includes the earlier bootstrap corrections.

No Gradle invocation, Java compilation or game execution was performed by the
assistant. The next user build is still required to confirm compilation and
expose any subsequent errors. Static success is not a clean-build claim.

Extract over the original project root, replacing matching files, then run:

```powershell
.\gradlew.bat clean build --warning-mode=fail
```

# Português do Brasil

Revisão: **Fix 2**, 25/09/2026.

O build informado chegou a compileJava e falhou porque GsonBuilder.class do
Gson 2.14.0 referencia com.google.errorprone.annotations.InlineMe, ausente no
classpath de compilação. Javac informou a ausência dos membros replacement()
e imports(), e -Werror interrompeu a compilação.

A correção adiciona error_prone_annotations 2.50.0 em compileOnly e
clientCompileOnly. O metadata do Maven Central foi consultado; 2.50.0 era a
versão numérica estável mais recente listada na conferência. O POM publicado
do Gson 2.14.0 declara 2.48.0; a versão mais nova selecionada preserva os métodos
necessários. O jar 2.50.0 foi inspecionado: InlineMe é uma anotação com
replacement(): String, imports(): String[] e staticImports(): String[].
URL e SHA-256 do artefato constam em dependency-fix2.json.

-Xlint:all, -Werror e warning.mode=fail continuam ativos. Não foi adicionado
processador de anotações nem mod de execução. Nenhum jar de dependência é
incluído no pacote-fonte.

A validação desta entrega inclui scan global estático, inspeção da classe e
assinaturas, comparação com o manifesto, testes independentes de ZIP/CRC e
comparação da cópia disponibilizada com o SHA-256 anterior ao envio. O pacote
completo mantém as correções anteriores do inicializador.

Não executei Gradle, compilação Java nem Minecraft. Seu próximo build ainda
é necessário para confirmar a compilação e identificar eventuais erros
seguintes. Aprovação estática não significa build confirmado sem erros.

Extraia por cima da raiz do projeto, substituindo os arquivos, e execute:

```powershell
.\gradlew.bat clean build --warning-mode=fail
```
