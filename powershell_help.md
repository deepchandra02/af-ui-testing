To enable your PowerShell script (`main.ps1`) to share variables with the `.cmd` scripts in the `deploy` folder, you can pass the variables as **environment variables**. Environment variables are accessible across different processes, including `.cmd` scripts.

Here’s how you can do it:

---

### **1. Set Environment Variables in PowerShell**

You can set environment variables in PowerShell that your `.cmd` scripts can read.

#### Main Script (`main.ps1`):

```powershell
# Define variables
$Variable1 = "Value1"
$Variable2 = "Value2"

# Set them as environment variables
[System.Environment]::SetEnvironmentVariable("Variable1", $Variable1, [System.EnvironmentVariableTarget]::Process)
[System.Environment]::SetEnvironmentVariable("Variable2", $Variable2, [System.EnvironmentVariableTarget]::Process)

# Execute the .cmd scripts
Get-ChildItem -Path "./deploy" -Filter "*.cmd" | ForEach-Object {
    & $_.FullName
}
```

---

### **2. Access Environment Variables in `.cmd` Scripts**

In your `.cmd` scripts, you can access these environment variables using `%VARIABLE_NAME%`.

#### Deploy Script (`deploy/script1.cmd`):

```cmd
@echo off
echo Variable1: %Variable1%
echo Variable2: %Variable2%
```

When the PowerShell script runs, the `.cmd` scripts will have access to `Variable1` and `Variable2`.

---

### **3. Example Output**

Assuming the setup above:

#### `main.ps1`:

```powershell
$Variable1 = "Hello"
$Variable2 = "World"

[System.Environment]::SetEnvironmentVariable("Variable1", $Variable1, [System.EnvironmentVariableTarget]::Process)
[System.Environment]::SetEnvironmentVariable("Variable2", $Variable2, [System.EnvironmentVariableTarget]::Process)

Get-ChildItem -Path "./deploy" -Filter "*.cmd" | ForEach-Object {
    & $_.FullName
}
```

#### `deploy/script1.cmd`:

```cmd
@echo off
echo Variable1: %Variable1%
echo Variable2: %Variable2%
```

#### Output:

```plaintext
Variable1: Hello
Variable2: World
```

---

### **4. Notes**

- **Scope of Environment Variables:** Using `[System.EnvironmentVariableTarget]::Process` ensures that the variables are set only for the current PowerShell session and any child processes it spawns (e.g., `.cmd` scripts). They won't persist globally or across sessions.
- **Security Consideration:** Ensure sensitive data (e.g., passwords) are not stored in environment variables unless necessary, as they can be accessed by any child process.

This approach ensures seamless communication between your PowerShell and `.cmd` scripts.
