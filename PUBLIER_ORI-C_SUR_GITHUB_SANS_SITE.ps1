param(
    [string]$ArchivePath = "",
    [string]$RepositoryUrl = "https://github.com/dalozedidier-dot/ORI-C.git",
    [string]$Branch = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Invoke-Git {
    param(
        [string[]]$Arguments,
        [string]$WorkingDirectory = ""
    )
    if ($WorkingDirectory) { Push-Location $WorkingDirectory }
    try {
        & git @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "La commande Git a échoué : git $($Arguments -join ' ')"
        }
    }
    finally {
        if ($WorkingDirectory) { Pop-Location }
    }
}

function Invoke-Python {
    param(
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )
    Push-Location $WorkingDirectory
    try {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3 @Arguments
        }
        elseif (Get-Command python -ErrorAction SilentlyContinue) {
            & python @Arguments
        }
        else {
            throw "Python 3 est introuvable. Installe Python puis relance ce fichier."
        }
        if ($LASTEXITCODE -ne 0) {
            throw "La commande Python a échoué : $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

function Find-CanonicalArchive {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        $resolved = Resolve-Path -LiteralPath $RequestedPath -ErrorAction Stop
        return $resolved.Path
    }

    $scriptDirectory = $PSScriptRoot
    $userProfile = [Environment]::GetFolderPath("UserProfile")
    $searchDirectories = @(
        $scriptDirectory,
        (Join-Path $userProfile "Downloads"),
        (Join-Path $userProfile "Desktop")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

    $found = foreach ($directory in $searchDirectories) {
        Get-ChildItem -LiteralPath $directory -File -Filter "ORI-C-v0.9.3-research-canonique*.zip" -ErrorAction SilentlyContinue
    }
    $selected = $found | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($selected) {
        return $selected.FullName
    }

    try {
        Add-Type -AssemblyName System.Windows.Forms
        $dialog = New-Object System.Windows.Forms.OpenFileDialog
        $dialog.Title = "Sélectionner l'archive canonique ORI-C v0.9.3"
        $dialog.Filter = "Archive ORI-C (*.zip)|*.zip"
        $dialog.Multiselect = $false
        if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
            return $dialog.FileName
        }
    }
    catch {
        # Le message final ci-dessous reste suffisamment explicite.
    }

    throw "Archive introuvable. Place ORI-C-v0.9.3-research-canonique.zip dans le même dossier que ce script, ou relance avec -ArchivePath."
}

$workRoot = $null
try {
    Write-Step "Vérification des outils"
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git est introuvable. Installe Git for Windows puis relance ce fichier."
    }
    & git lfs version *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Git LFS est introuvable. Installe Git LFS puis relance ce fichier."
    }

    $archive = Find-CanonicalArchive -RequestedPath $ArchivePath
    Write-Host "Archive utilisée : $archive"

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $workRoot = Join-Path $env:TEMP "ORI-C-publication-$stamp"
    $repoDirectory = Join-Path $workRoot "repo"
    $extractDirectory = Join-Path $workRoot "archive"
    $backupDirectory = Join-Path $workRoot "site-preserve"
    New-Item -ItemType Directory -Path $workRoot, $extractDirectory, $backupDirectory -Force | Out-Null

    Write-Step "Clonage du dépôt GitHub"
    $previousSkipSmudge = $env:GIT_LFS_SKIP_SMUDGE
    $env:GIT_LFS_SKIP_SMUDGE = "1"
    try {
        Invoke-Git -Arguments @("-c", "core.autocrlf=false", "clone", "--branch", $Branch, "--single-branch", $RepositoryUrl, $repoDirectory)
    }
    finally {
        if ($null -eq $previousSkipSmudge) {
            Remove-Item Env:GIT_LFS_SKIP_SMUDGE -ErrorAction SilentlyContinue
        }
        else {
            $env:GIT_LFS_SKIP_SMUDGE = $previousSkipSmudge
        }
    }
    Invoke-Git -Arguments @("config", "core.autocrlf", "false") -WorkingDirectory $repoDirectory
    Invoke-Git -Arguments @("lfs", "install", "--local") -WorkingDirectory $repoDirectory
    Invoke-Git -Arguments @("config", "user.name", "dalozedidier-dot") -WorkingDirectory $repoDirectory
    Invoke-Git -Arguments @("config", "user.email", "255488578+dalozedidier-dot@users.noreply.github.com") -WorkingDirectory $repoDirectory

    Write-Step "Extraction de l'archive canonique"
    Expand-Archive -LiteralPath $archive -DestinationPath $extractDirectory -Force
    $topItems = @(Get-ChildItem -LiteralPath $extractDirectory -Force)
    $topDirectories = @($topItems | Where-Object { $_.PSIsContainer })
    $topFiles = @($topItems | Where-Object { -not $_.PSIsContainer })
    if ($topDirectories.Count -eq 1 -and $topFiles.Count -eq 0) {
        $sourceDirectory = $topDirectories[0].FullName
    }
    else {
        $sourceDirectory = $extractDirectory
    }

    Write-Step "Sauvegarde stricte du site actuel"
    $sitePath = Join-Path $repoDirectory "site"
    $pagesWorkflowPath = Join-Path $repoDirectory ".github\workflows\pages.yml"
    $siteBackupPath = Join-Path $backupDirectory "site"
    $pagesBackupPath = Join-Path $backupDirectory "pages.yml"
    $siteOriginallyExists = Test-Path -LiteralPath $sitePath
    $pagesOriginallyExists = Test-Path -LiteralPath $pagesWorkflowPath
    if ($siteOriginallyExists) {
        Copy-Item -LiteralPath $sitePath -Destination $siteBackupPath -Recurse -Force
    }
    if ($pagesOriginallyExists) {
        Copy-Item -LiteralPath $pagesWorkflowPath -Destination $pagesBackupPath -Force
    }

    Write-Step "Remplacement complet du dépôt hors site"
    Get-ChildItem -LiteralPath $repoDirectory -Force |
        Where-Object { $_.Name -ne ".git" } |
        Remove-Item -Recurse -Force

    Get-ChildItem -LiteralPath $sourceDirectory -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $repoDirectory -Recurse -Force
    }

    # Le site et son workflow GitHub Pages restent exactement ceux du dépôt distant.
    if (Test-Path -LiteralPath $sitePath) {
        Remove-Item -LiteralPath $sitePath -Recurse -Force
    }
    if ($siteOriginallyExists) {
        Copy-Item -LiteralPath $siteBackupPath -Destination $sitePath -Recurse -Force
    }

    if (Test-Path -LiteralPath $pagesWorkflowPath) {
        Remove-Item -LiteralPath $pagesWorkflowPath -Force
    }
    if ($pagesOriginallyExists) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $pagesWorkflowPath) -Force | Out-Null
        Copy-Item -LiteralPath $pagesBackupPath -Destination $pagesWorkflowPath -Force
    }

    # Nettoyage des fichiers temporaires qui ne doivent jamais être publiés.
    $unwantedPaths = @(
        "MISE_A_JOUR_SITE.diff",
        "APPLIQUER_CORRECTIF.ps1",
        "APPLIQUER_CORRECTIF.sh",
        "LICENSE_PENDING.md",
        "MISE_A_JOUR.txt",
        "01_branche_matiere\hypergraphe_transformations\reclassement_relations.zip"
    )
    foreach ($relativePath in $unwantedPaths) {
        $absolutePath = Join-Path $repoDirectory $relativePath
        if (Test-Path -LiteralPath $absolutePath) {
            Remove-Item -LiteralPath $absolutePath -Recurse -Force
        }
    }

    Write-Step "Régénération et vérification des manifestes"
    Invoke-Python -Arguments @("build_manifest.py", "build") -WorkingDirectory $repoDirectory
    Invoke-Python -Arguments @("build_manifest.py", "verify") -WorkingDirectory $repoDirectory
    Invoke-Python -Arguments @("verifier_dossier.py") -WorkingDirectory $repoDirectory

    Write-Step "Contrôle de protection du site"
    & git -C $repoDirectory diff --quiet -- site .github/workflows/pages.yml
    if ($LASTEXITCODE -ne 0) {
        throw "Protection déclenchée : le site ou pages.yml a changé. Aucun commit n'a été envoyé."
    }

    Write-Step "Préparation du commit"
    Invoke-Git -Arguments @("add", "-A") -WorkingDirectory $repoDirectory
    & git -C $repoDirectory diff --cached --quiet -- site .github/workflows/pages.yml
    if ($LASTEXITCODE -ne 0) {
        throw "Protection déclenchée : le site apparaît dans le commit. Aucun envoi n'a été effectué."
    }

    & git -C $repoDirectory diff --cached --quiet
    $hasChanges = ($LASTEXITCODE -ne 0)
    if ($hasChanges) {
        Invoke-Git -Arguments @("commit", "-m", "release: publier ORI-C v0.9.3-research") -WorkingDirectory $repoDirectory
        Write-Step "Envoi du dépôt sur GitHub"
        Invoke-Git -Arguments @("push", "origin", "HEAD:$Branch") -WorkingDirectory $repoDirectory
    }
    else {
        Write-Host "Le dépôt est déjà identique à l'archive hors site. Aucun nouveau commit nécessaire." -ForegroundColor Yellow
    }

    $versionPath = Join-Path $repoDirectory "VERSION"
    if (Test-Path -LiteralPath $versionPath) {
        $version = (Get-Content -LiteralPath $versionPath -Raw).Trim()
        $tag = "v$version"
        $remoteTag = & git -C $repoDirectory ls-remote --tags origin "refs/tags/$tag"
        if ($LASTEXITCODE -ne 0) {
            throw "Impossible de vérifier le tag distant $tag."
        }
        if (-not $remoteTag) {
            Write-Step "Création du tag stable $tag"
            Invoke-Git -Arguments @("tag", "-a", $tag, "-m", "ORI-C $version") -WorkingDirectory $repoDirectory
            Invoke-Git -Arguments @("push", "origin", $tag) -WorkingDirectory $repoDirectory
        }
        else {
            Write-Host "Le tag $tag existe déjà. Il n'a pas été modifié." -ForegroundColor Yellow
        }
    }

    Write-Host "`nPUBLICATION TERMINÉE" -ForegroundColor Green
    Write-Host "Dépôt : https://github.com/dalozedidier-dot/ORI-C"
    Write-Host "Branche : $Branch"
    Write-Host "Le dossier site/ et .github/workflows/pages.yml n'ont pas été modifiés."

    Remove-Item -LiteralPath $workRoot -Recurse -Force
    $workRoot = $null
}
catch {
    Write-Host "`nÉCHEC : $($_.Exception.Message)" -ForegroundColor Red
    if ($workRoot -and (Test-Path -LiteralPath $workRoot)) {
        Write-Host "Dossier de diagnostic conservé : $workRoot" -ForegroundColor Yellow
    }
    Write-Host "Aucun site n'a été modifié par ce script." -ForegroundColor Yellow
    Read-Host "Appuie sur Entrée pour fermer"
    exit 1
}

Read-Host "Appuie sur Entrée pour fermer"
