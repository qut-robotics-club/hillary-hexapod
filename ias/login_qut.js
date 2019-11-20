const puppeteer = require("puppeteer-core");
(async () => {
  let browser;

  // try either google-chrome or chromium browser
  try {
    browser = await puppeteer.launch({ executablePath: "chromium-browser" });
  } catch (_) {
    browser = await puppeteer.launch({ executablePath: "google-chrome" });
  }

  const page = await browser.newPage();

  const navigationPromise = page.waitForNavigation();

  await page.goto(
    "https://esoe.qut.edu.au/auth/realms/qut/protocol/openid-connect/auth?response_type=code&client_id=shibboleth-2-idp&redirect_uri=https%3A%2F%2Fidp.qut.edu.au%2Fidp%2Fprofile%2FSAML2%2FPOST%2FSSO?execution%3De7s1%26_eventId_proceed%3D1&state=816757%2F8ee4e7ac-9a86-4a6d-9aec-9540e4f692ba&scope=openid"
  );

  await page.setViewport({ width: 1853, height: 981 });

  await navigationPromise;

  await navigationPromise;

  await page.waitForSelector("#loginSuccessful #username");
  await page.click("#loginSuccessful #username");

  await page.type("#loginSuccessful #username", "n9464263");

  await page.waitForSelector("#loginSuccessful #password");
  await page.click("#loginSuccessful #password");
  await page.type("#loginSuccessful #username", "Magnuman12");

  await page.waitForSelector(
    "div > #loginSuccessful > .form-group-container > .checkbox > label"
  );
  await page.click(
    "div > #loginSuccessful > .form-group-container > .checkbox > label"
  );

  await page.waitForSelector("#login-box-wrapper #kc-login");
  await page.click("#login-box-wrapper #kc-login");

  await navigationPromise;

  await navigationPromise;

  await browser.close();
})();
