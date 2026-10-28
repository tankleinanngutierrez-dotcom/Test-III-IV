document.addEventListener("alpine:init", () => {
  Alpine.store("theme", {
    dark: localStorage.getItem("medibook-theme") === "dark",
    toggle() { this.dark = !this.dark; localStorage.setItem("medibook-theme", this.dark ? "dark" : "light"); document.documentElement.classList.toggle("dark-mode", this.dark); }
  });
  document.documentElement.classList.toggle("dark-mode", Alpine.store("theme").dark);
  Alpine.store("toasts", {
    items: [], nextId: 1,
    add(message, type="info") { const item={id:this.nextId++,message,type}; this.items.push(item); setTimeout(()=>this.items=this.items.filter(t=>t.id!==item.id),4000); }
  });
  Alpine.data("bookingWizard", () => ({
    step:1, reasonLength:0,
    get stepLabel(){return ["Patient information","Choose a schedule","Review details"][this.step-1]},
    get canAdvance(){ if(this.step===1) return !!document.querySelector("#id_patient_name")?.value.trim() && !!document.querySelector("#id_phone")?.value.trim(); if(this.step===2) return !!document.querySelector("#id_appointment_date")?.value && !!document.querySelector("#id_time_slot")?.value; return this.reasonLength>=10; },
    init(){const reason=document.querySelector("#id_reason"); if(reason){this.reasonLength=reason.value.length;reason.addEventListener("input",()=>this.reasonLength=reason.value.length)} this.$watch("step",()=>this.$nextTick(()=>{document.querySelector(".form-card")?.scrollIntoView({behavior:"smooth",block:"nearest"})}));},
    nextStep(button){if(!this.canAdvance){this.$store.toasts.add("Please complete the required fields before continuing.","error");return;}this.step=Math.min(3,this.step+1);}
  }));
  Alpine.data("appointmentTabs", () => ({
    active:"All", statuses:["All","Pending","Confirmed","Cancelled"],
    get counts(){const rows=[...document.querySelectorAll("#appointment-rows tr[data-status]")];return {"All":rows.length,"Pending":rows.filter(r=>r.dataset.status==="Pending").length,"Confirmed":rows.filter(r=>r.dataset.status==="Confirmed").length,"Cancelled":rows.filter(r=>r.dataset.status==="Cancelled").length};}
  }));
});
document.body.addEventListener("toast", event => { if (window.Alpine) Alpine.store("toasts").add(event.detail.message || "Action completed", event.detail.type || "success"); });
document.body.addEventListener("htmx:beforeRequest", () => document.body.classList.add("is-loading"));
document.body.addEventListener("htmx:afterRequest", () => document.body.classList.remove("is-loading"));
