const BASE_URL = "https://of-by-for-the-people.herokuapp.com/";
class GovernorDuties {
  constructor() {
    this.newItem = null;
    this.newRoleBtn = null;
    this.itemList = null;
    this.formVisible = false;
    this.itemsExist = false;
  }
  init() {
    // window.addEventListener("DOMContentLoaded", () => {
    this.itemList = document.querySelector(".item-list");
    this.newRoleBtn = document.querySelector(".add-new-role-btn");
    this.newItem = document.querySelector(".new-item");
    this.newDutyForm = document.querySelector(".new-duty-form");
    this.newDutyForm.onsubmit = this.submitForm.bind(this);
    this.newItem.addEventListener("click", () => {
      this.formVisible
        ? (this.newDutyForm.style.display = "none")
        : (this.newDutyForm.style.display = "block");
      this.formVisible = !this.formVisible;
    });
    this.newRoleBtn.addEventListener("click", () => {
      this.formVisible
        ? (this.newDutyForm.style.display = "none")
        : (this.newDutyForm.style.display = "block");
      this.formVisible = !this.formVisible;
    });

    this.getGovrRoles();
    // });
  }
  submitForm(event) {
    event.preventDefault();
    let nameInput = document.querySelector("input[name='name']");
    let dutyInput = document.querySelector("input[name='duty']");
    const data = `name=${encodeURIComponent(
      nameInput.value
    )}&duty=${encodeURIComponent(dutyInput.value)}`;

    nameInput.innerHTML = "";
    dutyInput.innerHTML = "";

    fetch(BASE_URL + "governors", {
      method: "POST",
      body: data,
      credentials: "include",
      headers: {
        "Content-type": "application/x-www-form-urlencoded"
      }
    }).then(() => {
      console.log("Governor duty saved");
      this.getGovrRoles();
    });
  }
  getGovrRoles() {
    fetch(BASE_URL + "governors", { credentials: "include" }).then(response => {
      if (response.status == 401) {
        return 401;
      }
      response.json().then(data => {
        console.log("data is ", data);
        console.log("data length is ", data.length);
        const itemList = this.itemList.querySelectorAll(".item");
        console.log("itemList is ", itemList);
        console.log("itemlist length is ", itemList.length - 1);

        itemList.forEach((item, i) => {
          if (i > 0) {
            console.log(item);
            item.remove();
          }
        });

        data.forEach(item => {
          const card = document.querySelector(".item");
          const dupNode = card.cloneNode(true);
          dupNode.style.display = "block";

          const govrNameEl = dupNode.querySelector(".governor-name");
          govrNameEl.innerHTML = `Governor ${item.name}`;

          const govrDutiesEl = dupNode.querySelector(".governor-promises");
          const dutyEl = document.createElement("li");
          dutyEl.innerHTML = item.duties;
          govrDutiesEl.appendChild(dutyEl);

          const delBtn = dupNode.querySelector(".delete");
          delBtn.onclick = () => {
            const proceed = confirm(
              `Do you want to delete Governor ${item.name}'s duty?`
            );
            if (proceed) {
              this.deleteRole(item.id);
            }
          };

          this.itemList.appendChild(dupNode);

          const editBtn = dupNode.querySelector(".edit");
          editBtn.onclick = () => {
            console.log("edit role");
            this.editRole(dupNode, item.id);
          };
        });
      });
    });
  }

  editRole(node, id) {
    const card = document.querySelector(".new-duty-form");
    const form = card.cloneNode(true);
    form.style.display = "block";

    const addBtn = form.querySelector(".add-new-role-btn");
    addBtn.innerHTML = "Submit";

    const govrNameEl = form.querySelector("input[name='name']");
    const govrDutiesEl = form.querySelector("input[name='duty']");

    this.preFillForm(id, govrNameEl, govrDutiesEl);

    form.onsubmit = event => {
      event.preventDefault();
      const data = `name=${encodeURIComponent(
        govrNameEl.value
      )}&duty=${encodeURIComponent(govrDutiesEl.value)}`;

      fetch(`http://localhost:8080/governors/${id}`, {
        method: "PUT",
        body: data,
        credentials: "include",
        headers: {
          "Content-type": "application/x-www-form-urlencoded"
        }
      }).then(() => {
        console.log("Governor duty saved");
        this.getGovrRoles();
      });
      form.style.display = "none";
    };
    node.appendChild(form);
  }

  preFillForm(id, nameEl, dutiesEl) {
    fetch(`http://localhost:8080/governors/${id}`, {
      credentials: "include"
    }).then(response => {
      response.json().then(data => {
        nameEl.value = data.name;
        dutiesEl.value = data.duties;
      });
    });
  }

  deleteRole(id) {
    fetch(`http://localhost:8080/governors/${id}`, {
      method: "DELETE",
      credentials: "include"
    }).then(response => {
      console.log("Governor role deleted");
      this.getGovrRoles();
    });
  }
}

class User extends GovernorDuties {
  constructor() {
    super();
    this.switchEl = document.querySelector("#login-register-switch");
    this.fNameEl = document.querySelector("#first_name");
    this.lNameEl = document.querySelector("#last_name");
    this.pWordEl = document.querySelector("#password");
    this.emailEl = document.querySelector("#email");
    this.loginFormEl = document.querySelector(".container-login");
    this.registerFormEl = document.querySelector(".container-register");
    this.postsEl = document.querySelector(".container-posts");
    this.fName = "";
    this.lName = "";
    this.email = "";
    this.password = "";
    this.loginVisible = true;
    this.postVisible = false;
  }

  init() {
    window.addEventListener("DOMContentLoaded", () => {
      // depending on whether the user is logged in
      // show the appropriate page
      fetch(BASE_URL + "governors", { credentials: "include" }).then(
        response => {
          if (response.status == 401) {
            // display login form
            const body = document.querySelector("body");
            body.style.display = "block";
            console.log("User not logged in, display login form");
            const registerBtn = document.querySelector("#register");
            registerBtn.addEventListener("click", () => {
              this.getFormInput("register");
              this.registerUser();
            });
            const loginBtn = document.querySelector("#login");
            loginBtn.addEventListener("click", () => {
              this.getFormInput("login");
              this.loginUser();
            });

            this.switchEl.addEventListener("click", () => {
              this.switchForm();
            });
          } else {
            // display data
            const body = document.querySelector("body");
            body.style.display = "block";
            console.log("User is logged in, display data");
            this.loginFormEl.style.display = "none";
            this.switchEl.style.display = "none";
            this.postsEl.style.display = "block";
            this.postVisible = true;
            this.logOutEl = document.querySelector("#log-out");
            console.log(this.logOutEl);
            this.logOutEl.onclick = () => {
              this.logOut();
            };
            super.init();
          }
        }
      );
    });
  }

  logOut() {
    fetch(BASE_URL + "logout", {
      method: "POST",
      credentials: "include"
    }).then(response => {
      if (response.status == 201) {
        alert("Log out successful");
        this.switchForm();
      } else {
        alert("error while trying to log out");
      }
    });
  }

  getFormInput(formType) {
    if (formType == "login") {
      this.pWordEl = document.querySelector(".container-login #password");
      this.emailEl = document.querySelector(".container-login #email");
    } else {
      this.fNameEl = document.querySelector(".container-register #first_name");
      this.lNameEl = document.querySelector(".container-register #last_name");
      this.pWordEl = document.querySelector(".container-register #password");
      this.emailEl = document.querySelector(".container-register #email");
    }

    this.fName = this.fNameEl.value;
    this.lName = this.lNameEl.value;
    this.email = this.emailEl.value;
    this.password = this.pWordEl.value;
  }

  loginUser() {
    const data = `email=${encodeURIComponent(
      this.email
    )}&password=${encodeURIComponent(this.password)}`;

    fetch(BASE_URL + "sessions", {
      method: "POST",
      body: data,
      headers: {
        "Content-type": "application/x-www-form-urlencoded"
      },
      credentials: "include"
    }).then(response => {
      console.log(response.status);
      if (response.status == 201 || response.status == 200) {
        console.log("login user");
        this.loginFormEl.style.display = "none";
        this.switchEl.style.display = "none";
        this.postsEl.style.display = "block";
        super.init();
      } else {
        if (response.status == 401) {
          alert("Incorrect password");
        }
        // this.clearContent([this.emailEl, this.pWordEl]);
      }
    });
  }

  registerUser() {
    const data = `fName=${encodeURIComponent(
      this.fName
    )}&lName=${encodeURIComponent(this.lName)}&email=${encodeURIComponent(
      this.email
    )}&password=${encodeURIComponent(this.password)}`;

    fetch(BASE_URL + "users", {
      method: "POST",
      body: data,
      headers: {
        "Content-type": "application/x-www-form-urlencoded"
      },
      credentials: "include"
    }).then(response => {
      console.log(response.status);
      if (response.status == 201 || response.status == 200) {
        alert("You have been successfully registered");
        this.clearContent([
          this.emailEl,
          this.pWordEl,
          this.fNameEl,
          this.lNameEl
        ]);
        this.switchForm();
        // this.switchEl.style.display = "none";
        // this.postsEl.style.display = "block";
        // super.init();
      } else {
        if (response.status == 422) {
          alert("This email already exists");
        }
      }
    });
  }

  switchForm() {
    if (this.postVisible) {
      // this.switchEl.style.display = "block";
      this.loginFormEl.style.display = "block";
      this.switchEl.style.display = "block";
      this.postsEl.style.display = "none";
    }
    if (this.loginVisible) {
      this.loginFormEl.style.display = "none";
      this.registerFormEl.style.display = "block";
      this.loginVisible = !this.loginVisible;
      this.switchEl.innerHTML = "Login Form";
    } else {
      this.registerFormEl.style.display = "none";
      this.loginFormEl.style.display = "block";
      this.loginVisible = !this.loginVisible;
      this.switchEl.innerHTML = "Register Form";
    }
  }

  clearContent(elements) {
    for (const i in elements) {
      elements[i].value = "";
    }
  }
}

const user = new User();
user.init();
