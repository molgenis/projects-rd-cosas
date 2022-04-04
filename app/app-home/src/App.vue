<template>
  <div id="portal">
    <header id="portal-header" class="jumbotron">
      <div class="header-content">
        <h1>Genetica Diagnostics Portal</h1>
        <h2>Find, explore, and access data</h2>
      </div>
      <div class="header-filter" aria-hidden="true"></div>
    </header>
    <main>
      <section id="portal-welcome" aria-labelledby="portal-welcome-title">
        <div class="col-sm-8 m-auto">
          <h2 id="portal-welcome-title" class="text-center">Welcome</h2>
          <p>
            Welcome to the <strong>Genetica Diagnostics Portal</strong>! With this site, you can
            access a number of databases and systems available to members of the
            genetica department developed by the Molgenis team.
          </p>
        </div>
      </section>
      <section id="portal-databases" aria-labelledby="portal-databases-title">
        <div class="col-sm-8 m-auto">
          <h2 class="text-center">View Databases</h2>
          <p>
            Sign in to any of the following databases using your UMCG
            credentials. If you have been given access to a system and it isn't
            in the list below, contact
            <a href="mailto:molgenis-support@umcg.nl"
              >molgenis-support@umcg.nl</a
            >.
          </p>
        </div>
        <div id="db-card-container" class="d-flex flex-wrap justify-content-md-center">
          <div class="card col-md-3">
            <div class="card-body">
              <h3 class="card-title">COSAS</h3>
              <p class="card-text">
                View the Catalog of Sequences, Arrays, and Samples.
              </p>
              <a href="/menu/main/navigator/umdm" class="btn btn-dark btn-block">
                View
              </a>
            </div>
          </div>
          <div class="card col-md-3">
            <div class="card-body">
              <h3 class="card-title">Unsolved Cases</h3>
              <p class="card-text">
                View and submit new cases to the Unsolved Cases Portal.
              </p>
              <a href="/menu/main/navigator/ucu" class="btn btn-dark btn-block">
                View
              </a>
            </div>
          </div>
          <div class="card col-md-3">
            <div class="card-body">
              <h3 class="card-title">VariantDB</h3>
              <p class="card-text">
                Find and explore variants in the Variants database.
              </p>
              <a href="/menu/main/navigator/variantdb" class="btn btn-dark btn-block">View</a>
            </div>
          </div>
        </div>
      </section>
      <section id="portal-help" aria-labelledby="portal-help-title">
        <div class="col-md-4 m-auto">
          <h2 id="portal-help-title" class="text-center">Get help</h2>
          <p>Need help? Do you have a question? If so, please contact the support desk.</p>
          <a href="mailto:molgenis-support@umcg.nl" class="btn btn-dark btn-block">Contact Support</a>
        </div>
      </section>
    </main>
    <div id="portal-footer" class="bg-dark footer">
      <img :src="MolgenisLogo" alt="molgenis open source data platform" class="molgenis-logo"/>
    </div>
  </div>
</template>

<script>

export default {
  data () {
    return {
      logged: false,
      MolgenisLogo: require('../src/assets/Logo_Blue_Small.png')
    }
  }
}
</script>

<style lang="scss">

.mg-page,
.mg-app,
.container-fluid,
.row,
.col-sm-8,
.col-sm-3 {
  padding: 0;
  
}

h1,h2,h3,h4,h5,h6 {
  color: #252525;
}

.mg-page .mg-page-content {
  margin-top: 0;
}

footer.footer {
  display: none;
  padding: 0;
  margin: 0;
}

#portal {
  color: #3f454b;

  section, .footer {
    padding: 2em 1em;
  }
}
  
#portal-header {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  border: none;
  border-radius: 0;
  height: 22em;
  background: none;
  background-position: 100% 0;
  background-size: cover;
  background-image: url("~@/assets/header-bg-2.jpg");

  .header-filter {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: hsla(0, 0%, 0%, 0.3);
  }

  .header-content {
    width: 100%;
    height: 100%;
    z-index: 1;
    color: #f6f6f6;
    
    h1, h2 {
      color: inherit;
    }
    
    h1 {
      font-size: 13pt;
      text-transform: uppercase;
      letter-spacing: 4px;
      font-weight: bold;
    }
    
    h2 {
      font-size: 32pt;
      font-weight: 200;
    }
  }
}

.molgenis-logo {
  width: 124px;
}

#portal-databases {
  background-color: #f6f6f6;
}

#db-card-container {
  padding: 1em 0;
  gap: 12px;
  .card {
    .card-title {
      font-size: 11pt;
      text-transform: uppercase;
      font-weight: bold;
      letter-spacing: 2px;
    }
  }
}

</style>
