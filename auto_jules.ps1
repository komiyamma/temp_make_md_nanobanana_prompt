Param(
    [string]$Range,
    [switch]$Loop
)

# --- 設定 ---
$API_KEY = $env:JULES_API_KEY
$HEADERS = @{
    "X-Goog-Api-Key" = $API_KEY
    "Content-Type"   = "application/json"
}
$BASE_URL = "https://jules.googleapis.com/v1alpha"

function Run-JulesForRange {
    param([string]$targetRange)

    if ($targetRange -notmatch '^\s*(\d+)\s*-\s*(\d+)\s*$') {
        Write-Error "形式が違います: $targetRange"
        return
    }

    $startLine = [int]$Matches[1]
    $endLine = [int]$Matches[2]
    if ($startLine -gt $endLine) { 
        Write-Error "開始行は終了行以下にしてください: $targetRange"
        return
    }

    Write-Host "`n===============================================" -ForegroundColor Gray
    Write-Host "🎯 処理開始: 範囲 $targetRange" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Gray

    # 1. セッションの開始
    Write-Host "🚀 Jules セッションを開始します..." -ForegroundColor Cyan
    $body = @{
        prompt              = "gemini_command.md $startLine-$endLine"
        sourceContext       = @{
            source            = "sources/github/komiyamma/temp_make_md_nanobanana_prompt"
            githubRepoContext = @{ startingBranch = "main" }
        }
        requirePlanApproval = $false
        automationMode      = "AUTO_CREATE_PR"
        title               = "MDのnano banana 用の画像生成計画を立てる。($targetRange)"
    } | ConvertTo-Json -Depth 10

    $session = Invoke-RestMethod -Uri "$BASE_URL/sessions" -Method Post -Headers $HEADERS -Body $body
    $sessionName = $session.name
    $sessionId = if ($sessionName -match '^sessions/(.+)$') { $Matches[1] } else { $sessionName }
    Write-Host "✅ セッション作成完了: $sessionName"

    # 2. 3分おきに完了チェック（最大10回）
    $maxChecks = 15
    $checkCount = 0
    $isCompleted = $false
    $maxChecksReached = $false
    Write-Host "⏳ 作業完了を待機中（2分間隔、最大$maxChecks回）..." -ForegroundColor Yellow
    while ($true) {
        $checkCount++
        $current = Invoke-RestMethod -Uri "$BASE_URL/$sessionName" -Headers $HEADERS
        Write-Host "$(Get-Date -Format 'HH:mm:ss') - 現在のステータス: $($current.state)"
        
        if ($current.state -eq "COMPLETED") {
            $isCompleted = $true
            Write-Host "🎉 Jules の作業が正常に完了しました。" -ForegroundColor Green
            break
        }
        elseif ($current.state -eq "FAILED" -or $current.state -eq "CANCELLED") {
            Write-Error "❌ Jules の作業が失敗またはキャンセルされました。 (State: $($current.state))"
            return
        }

        if ($checkCount -ge $maxChecks) {
            Write-Warning "⌛ 最大確認回数（$maxChecks回）に到達したため、範囲 $targetRange をスキップします。"
            $maxChecksReached = $true
            break
        }

        Start-Sleep -Seconds 120
    }

    if ($maxChecksReached) {
        Write-Host "🛑 セッションを強制終了します: $sessionName" -ForegroundColor Yellow
        try {
            Invoke-RestMethod -Uri "$BASE_URL/sessions/$sessionId" -Method Delete -Headers $HEADERS | Out-Null
            Write-Host "✅ セッションを削除しました: $sessionName" -ForegroundColor Yellow
        }
        catch {
            Write-Warning "⚠️ セッション削除に失敗しました: $sessionName / $($_.Exception.Message)"
        }
        return
    }

    if (-not $isCompleted) {
        return
    }

    # 4. GitHub CLI (gh) を使った操作
    $sessionInfo = Invoke-RestMethod -Uri "$BASE_URL/$sessionName" -Headers $HEADERS
    $prUrl = $sessionInfo.output.pullRequest.url

    if (-not $prUrl) {
        Write-Warning "PR URL が取得できませんでした。gh コマンドで最新の PR を探します。"
        $prUrl = gh pr list --repo "komiyamma/temp_make_md_nanobanana_prompt" --limit 1 --json url --jq ".[0].url"
    }

    Write-Host "🛠️ PR 承認とマージを実行します: $prUrl" -ForegroundColor Cyan
    gh pr edit $prUrl --add-assignee "komiyamma"

    # --- Verification Step ---
    Write-Host "🔍 画像プランとHTMLの整合性を確認します..." -ForegroundColor Yellow
    
    # Switch to PR branch to verify content
    Write-Host "🔀 PRブランチをチェックアウトします..." -ForegroundColor Gray
    gh pr checkout $prUrl

    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ PRブランチのチェックアウトに失敗しました。"
        git checkout main
        return
    }

    # Run verification script
    python verify_image_plan_consistency.py
    $verifyResult = $LASTEXITCODE

    # Always return to main
    git checkout main

    if ($verifyResult -ne 0) {
        Write-Error "❌ 整合性チェックに失敗しました。PR ($prUrl) はマージされません。手動で確認してください。"
        return
    }

    Write-Host "✅ 整合性チェックに合格しました。マージを続行します。" -ForegroundColor Green
    # --- End Verification Step ---

    gh pr review $prUrl --approve --body "Approved by komiyamma automation script. Range: $targetRange"
    gh pr merge $prUrl --merge --delete-branch

    # 5. ローカルへの同期
    Write-Host "📥 ローカルの main ブランチを更新します..." -ForegroundColor Green
    git checkout main
    git pull origin main

    Write-Host "✨ 範囲 $targetRange の全工程が完了しました！" -ForegroundColor Green
}

# --- メインロジック ---
if ($Loop) {
    # 自動ループモード: 841-850 から 971-980 まで
    for ($i = 945; $i -le 971; $i += 6) {
        $r = "$i-$($i + 5)"
        Run-JulesForRange -targetRange $r
    }
}
elseif ($Range) {
    # 個別範囲指定モード
    Run-JulesForRange -targetRange $Range
}
else {
    # 従来モード (引数なし)
    $inputRange = Read-Host "範囲を入力（例: 221-230）"
    if ([string]::IsNullOrWhiteSpace($inputRange)) {
        Write-Warning "範囲が入力されませんでした。"
        exit
    }
    Run-JulesForRange -targetRange $inputRange
}
