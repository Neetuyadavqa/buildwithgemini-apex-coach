const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  console.log('Starting demo video recording for Apex Coach...');
  
  const artifactDir = '/config/.gemini/antigravity/brain/de348da7-991e-47cc-84df-a7bcc4e1d58e';
  if (!fs.existsSync(artifactDir)) fs.mkdirSync(artifactDir, { recursive: true });

  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: {
      dir: artifactDir,
      size: { width: 1280, height: 800 }
    }
  });

  const page = await context.newPage();
  
  console.log('Navigating to Apex Coach Frontend...');
  await page.goto('https://apex-coach-frontend-242130559876.us-central1.run.app');
  await page.waitForTimeout(3000); // Highlight welcome card & header

  // --- Step 1: First Prompt (Marathon Workouts) ---
  console.log('Step 1: Typing first prompt for workout routines...');
  const input = page.locator('#input');
  const firstPrompt = 'Find workout routines for marathon training';
  
  await input.focus();
  await page.waitForTimeout(500);
  await page.keyboard.type(firstPrompt, { delay: 40 });
  await page.waitForTimeout(600);
  await page.keyboard.press('Enter');

  console.log('Waiting for workout routines response...');
  await page.waitForFunction(() => {
    const msgs = document.querySelectorAll('.msg.agent');
    if (msgs.length === 0) return false;
    const lastMsg = msgs[msgs.length - 1];
    return lastMsg.textContent && !lastMsg.textContent.includes('…');
  }, { timeout: 45000 });

  await page.waitForTimeout(4000); // Pause to read workout results

  // --- Step 2: Second Prompt (Rich prompt - Gear & Visual preview) ---
  console.log('Step 2: Typing second prompt for gear & image generation...');
  const secondPrompt = 'Recommend top trail running shoes for marathon training and generate a visual preview';
  
  await input.focus();
  await page.waitForTimeout(500);
  await page.keyboard.type(secondPrompt, { delay: 40 }); // Realistic typing
  await page.waitForTimeout(800);
  await page.keyboard.press('Enter');

  console.log('Waiting for gear recommendation & image generation response...');
  await page.waitForFunction(() => {
    const msgs = document.querySelectorAll('.msg.agent');
    if (msgs.length < 2) return false;
    const lastMsg = msgs[msgs.length - 1];
    return lastMsg.textContent && !lastMsg.textContent.includes('…');
  }, { timeout: 60000 });

  await page.waitForTimeout(3000);

  // Smooth scroll down to reveal image & final response
  console.log('Scrolling down to showcase generated visual...');
  await page.evaluate(() => {
    const log = document.getElementById('log');
    if (log) log.scrollTop = log.scrollHeight;
  });

  await page.waitForTimeout(5000); // Pause on final state

  // Close context to save video file
  const videoPath = await page.video().path();
  await page.close();
  await context.close();
  await browser.close();

  const finalVideo = path.join(artifactDir, 'apex_coach_demo.webm');
  if (videoPath !== finalVideo) {
    fs.copyFileSync(videoPath, finalVideo);
  }

  console.log(`Demo video successfully generated at: ${finalVideo}`);
})();
