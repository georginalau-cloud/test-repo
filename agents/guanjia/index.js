module.exports = {
  name: "guanjia",
  bootstrap: async function(core){
 console.log("[guanjia] bootstrap called");
  },
  start: async function(core){
 console.log("[guanjia] start called");
  },
  stop: async function(core){
 console.log("[guanjia] stop called");
  }
};
