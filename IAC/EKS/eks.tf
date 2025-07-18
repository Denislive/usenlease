module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.36.0"

  cluster_name    = "usenlease-eks"
  cluster_version = "1.30"
  subnet_ids      = module.vpc.private_subnets
  vpc_id          = module.vpc.vpc_id

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  eks_managed_node_group_defaults = {
    instance_types = ["t3.medium"]
  }

  eks_managed_node_groups = {
    default = {
      min_size     = 1
      max_size     = 3
      desired_size = 2
    }
  }

  authentication_mode = "API"

  access_entries = {
    kubestronaut = {
      principal_arn = "arn:aws:iam::472083777554:user/Kubestronaut"
      type          = "STANDARD"
      username      = "Kubestronaut"

      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

          access_scope = {
            type       = "cluster"
            namespaces = []
          }
        }
      }
    }
    
    root = {
      principal_arn = "arn:aws:iam::472083777554:root"
      type          = "STANDARD"
      username      = "root-user"

      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

          access_scope = {
            type       = "cluster"
            namespaces = []
          }
        }
      }
    }
  }

  tags = {
    Environment = "prod"
    Project     = "usenlease"
  }
}
