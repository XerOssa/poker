window._initResizeHandler = ({ originWidth, originHeight }) => {
    const { documentElement } = document;
    let prevRootFontSize;
    let prevWindowWidth;
    let prevWindowHeight;
  
    const updateRootFootSize = () => {
      const { clientWidth, clientHeight } = documentElement;
      const { innerWidth, innerHeight } = window;
      const width = Math.max(clientWidth, innerWidth || 0);
      const height = Math.max(clientHeight, innerHeight || 0);
      const windowWidth = `${width}px`;
      const windowHeight = `${height}px`;
      let rootFontSize;
      if (width / originWidth < height / originHeight) {
        rootFontSize = `calc(${width}px / ${originWidth})`;
      } else {
        rootFontSize = `calc(${height}px / ${originHeight})`;
      }
      if (prevRootFontSize !== rootFontSize) {
        documentElement.style.setProperty("--root-font-size", rootFontSize);
      }
      if (prevWindowWidth !== windowWidth) {
        documentElement.style.setProperty("--window-width", windowWidth);
      }
      if (prevWindowHeight !== windowHeight) {
        documentElement.style.setProperty("--window-height", windowHeight);
      }
      prevRootFontSize = rootFontSize;
      prevWindowWidth = windowWidth;
      prevWindowHeight = windowHeight;
    };
    window.addEventListener("resize", updateRootFootSize);
    updateRootFootSize();
  };
  
  const designSizes = {
    originWidth: 3840,
    originHeight: 2160
  };
  
  const deviceSizes = [
    { name: 'iPhone XS Max', width: 2688, height: 1242 },
    { name: 'iPhone XR', width: 1792 , height: 828 },
    { name: 'iPhone X, XS', width: 2436 , height: 1125  },
    { name: 'iPhone 4', width: 960 , height: 640 },
    { name: 'iPad Pro', width: 2732 , height: 2048 },
  ];
  
  const deviceInp = document.getElementById("deviceInp");
  deviceSizes.forEach((sizeData) => {
    const optionNode = document.createElement("option");
    const textnode = document.createTextNode(sizeData.name);
    optionNode.appendChild(textnode);
    deviceInp.appendChild(optionNode);
  });
  deviceInp.addEventListener("change", function() {
    console.log(deviceSizes.find((sizeData) => sizeData.name === deviceInp.value));
  });
  
  const originSizes = {
    originWidth: 3840,
    originHeight: 2160
  };
  
  const adjustSize = () => {
    console.log(originSizes);
    _initResizeHandler(originSizes);
    const layout = document.getElementsByClassName("layout")[0];
    console.log(layout);
    layout.style.cssText  = `
      width: ${originSizes.originWidth}rem;
      height: ${originSizes.originHeight}rem;
    `;
  };
  
  adjustSize();
  
  const widthInp = document.getElementById("widthInp");
  widthInp.addEventListener("input", evt => {
    originSizes.originWidth = Math.floor(+evt.target.value);
    adjustSize();
  });
  
  const heightInp = document.getElementById("heightInp");
  heightInp.addEventListener("input", evt => {
    originSizes.originHeight = Math.floor(+evt.target.value);
    adjustSize();
  });
  